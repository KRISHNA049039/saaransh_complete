import json
import asyncio
import logging
import litellm
from litellm import acompletion
from litellm.utils import token_counter

litellm.suppress_debug_info = True
for key in logging.Logger.manager.loggerDict.keys():
    if "litellm" in key.lower():
        logging.getLogger(key).setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


class LiteLLMAccessor:
    async def _build_messages(self, content: str, user_prompt: str, system_prompt: str):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        final_content = (
            f"user_instructions: {user_prompt}\n\n{content}" if user_prompt else content
        )

        messages.append({"role": "user", "content": final_content})
        return messages

    async def _run_tools(self, response_message, tool_registry):
        tool_calls = response_message.tool_calls or []
        if not tool_calls:
            return []

        logger.debug(f"--- LLM requested {len(tool_calls)} tool(s) ---")

        tasks = []
        call_ids = []

        for call in tool_calls:
            fn_name = call.function.name
            args = json.loads(call.function.arguments)
            call_ids.append(call.id)

            logger.debug(f"Running tool: {fn_name} with args: {args}")

            if fn_name in tool_registry:
                fn = tool_registry[fn_name]
                tasks.append(fn(**args))
            else:
                tasks.append(
                    asyncio.create_task(
                        asyncio.sleep(0, result=f"Error: Unknown tool '{fn_name}'")
                    )
                )

        results = await asyncio.gather(*tasks)

        return [
            {"role": "tool", "tool_call_id": call_ids[i], "content": results[i]}
            for i in range(len(results))
        ]

    async def get_response(
        self,
        model: str,
        content: str,
        user_prompt: str,
        system_prompt: str,
        use_tools: bool = False,
        tool_schemas=None,
        tool_registry=None,
    ):
        try:
            logger.debug(f"--- Using model: {model} (tools={use_tools}) ---")

            messages = await self._build_messages(content, user_prompt, system_prompt)

            # Initial request
            response = await acompletion(
                model=model,
                messages=messages,
                tools=tool_schemas if use_tools else None,
                tool_choice="auto" if use_tools else None,
            )

            response_message = response.choices[0].message

            if not use_tools or not response_message.tool_calls:
                return response_message.content

            # Execute tool calls
            tool_msgs = await self._run_tools(response_message, tool_registry)
            messages.append(response_message)
            messages.extend(tool_msgs)

            # Final response after tool results
            final_response = await acompletion(model=model, messages=messages)
            return final_response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling LiteLLM: {e}")
            raise

    async def get_token_count(self, model, text: str) -> int:
        try:
            messages = [{"role": "user", "content": text}]
            return token_counter(model=model, messages=messages)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return len(text) // 4
