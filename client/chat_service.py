import json
import traceback

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from client.config import MCP_SERVER_URL
from client.llm import GroqLLM


SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are a helpful assistant with access to MCP tools.

Rules:

- Decide whether a tool is needed.
- Use tools for current or external information.
- Never call the same tool repeatedly.
- Use the tool result to answer the user.
- Never invent information.

Email requests:
- Show the sender
- Show the subject
- Show the date
- Show the snippet

Calendar requests:
- Show the title
- Show the date
- Show the time
- Show the location

Meeting requests:
- Create only one meeting unless the user explicitly asks for multiple meetings.
- Join only one meeting.
""",
}


def _groq_tools(mcp_tools):

    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description
                or f"Run the {tool.name} MCP tool.",
                "parameters": tool.inputSchema,
            },
        }
        for tool in mcp_tools
    ]


async def chat(history):

    llm = GroqLLM()

    messages = [SYSTEM_MESSAGE, *history]

    tools_used = []

    try:

        async with streamablehttp_client(MCP_SERVER_URL) as (
            read_stream,
            write_stream,
            _,
        ):

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                available_tools = await session.list_tools()

                tools = _groq_tools(
                    available_tools.tools
                )

                max_steps = 3

                for _ in range(max_steps):

                    response = llm.chat(
                        messages,
                        tools,
                        tool_choice="auto",
                    )

                    assistant = (
                        response.choices[0].message
                    )

                    if not assistant.tool_calls:

                        return {
                            "message": assistant.content
                            or "No response generated.",
                            "tools_used": tools_used,
                        }

                    messages.append(
                        assistant.model_dump(
                            exclude_none=True
                        )
                    )

                    stop_workflow = False

                    for tool_call in assistant.tool_calls:

                        tool_name = (
                            tool_call.function.name
                        )

                        if tool_name in tools_used:

                            print(
                                f"Skipping repeated tool: "
                                f"{tool_name}"
                            )

                            stop_workflow = True
                            break

                        try:

                            arguments = json.loads(
                                tool_call.function.arguments
                                or "{}"
                            )

                        except Exception:

                            arguments = {}

                        print(
                            f"\nCalling tool: "
                            f"{tool_name}"
                        )

                        print(
                            f"Arguments: {arguments}"
                        )

                        try:

                            result = (
                                await session.call_tool(
                                    tool_name,
                                    arguments,
                                )
                            )

                        except Exception:

                            traceback.print_exc()

                            return {
                                "message": (
                                    f"Error while executing "
                                    f"{tool_name}"
                                ),
                                "tools_used": tools_used,
                            }

                        result_text = "\n".join(
                            item.text
                            for item in result.content
                            if hasattr(item, "text")
                        )

                        print(
                            "\n========== TOOL RESULT =========="
                        )

                        print(result_text)

                        print(
                            "=================================\n"
                        )

                        tools_used.append(tool_name)

                        if result.isError:

                            return {
                                "message": (
                                    f"The {tool_name} "
                                    f"tool failed:\n\n"
                                    f"{result_text}"
                                ),
                                "tools_used": tools_used,
                            }

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_text,
                            }
                        )

                    if stop_workflow:

                        break

                final_response = llm.chat(
                    messages,
                    [],
                    tool_choice="none",
                )

                return {
                    "message": (
                        final_response
                        .choices[0]
                        .message
                        .content
                    ),
                    "tools_used": tools_used,
                }

    except Exception:

        traceback.print_exc()

        return {
            "message": (
                "Error: unhandled errors in a TaskGroup."
            ),
            "tools_used": tools_used,
        }