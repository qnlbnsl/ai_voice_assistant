import json
from multiprocessing import Queue
from multiprocessing.synchronize import Event
import time
from typing import List, cast
from logger import logger
from assistant.assistants import (
    intent_assistant,
    threads,
    add_message_to_thread,
    run_thread,
    message_thread,
)
from assistant.parse_commands.hassio import handle_command

from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from openai.types.beta.threads.message_content_text import (
    MessageContentText as MessageContentText,
)

# HASSIO Bindings.


# TODO: Implement responses.
def parse_command(
    shutdown_event: Event,
    wake_word_event: Event,
    thinking_event: Event,
    intent_queue: "Queue[str]",
    response_queue: "Queue[str]",
) -> None:
    logger.info("Parse Command Ready")
    while shutdown_event.is_set() is False:
        intent = (
            intent_queue.get()
        )  # blocking operation. waits until there is an item in the queue.
        # let the client know that we are thinking.
        thinking_event.set()
        logger.debug(intent)
        intent_thread = threads.create()
        add_message_to_thread(thread_id=intent_thread.id, message=intent)
        run = run_thread.create(
            thread_id=intent_thread.id, assistant_id=intent_assistant.id
        )
        while (
            run.status != "completed"
            and run.status != "failed"
            and run.status != "expired"
        ):
            time.sleep(1)
            run = run_thread.retrieve(thread_id=intent_thread.id, run_id=run.id)
            logger.debug(run.status)
            if (
                run.status == "requires_action"
                and run.required_action
                and run.required_action.type == "submit_tool_outputs"
            ):
                tool_outputs: List[ToolOutput] = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    function_call_id = tool_call.id
                    function_name = tool_call.function.name
                    arguments = tool_call.function.arguments
                    logger.debug(function_call_id)
                    logger.debug(function_name)
                    logger.debug(arguments)
                    data = json.loads(arguments)
                    result = handle_command(
                        command=data["command"],
                        domain=data["domain"],
                        friendly_name=data["entity_id"],
                        temperature=data["temperature"],
                    )
                    tool_outputs.append(
                        {"tool_call_id": function_call_id, "output": str(result)}
                    )
                logger.debug(f"Submitting tool outputs: {tool_outputs}")
                run_thread.submit_tool_outputs(
                    thread_id=intent_thread.id, run_id=run.id, tool_outputs=tool_outputs
                )

        messages = message_thread.list(thread_id=intent_thread.id)
        result = "True"
        for message in messages.data:
            if message.role == "assistant":
                response = cast(MessageContentText, message.content[0])
                logger.debug(response.text.value)
                intent_queue.put(response.text.value)

        if result == "True":
            threads.delete(thread_id=intent_thread.id)
        else:
            logger.debug("Result was not true. Not deleting thread.")
            response_queue.put(
                "Error in command execution. Failed to {data['command']} the {data['domain']} {data['entity_id']}."
            )
        wake_word_event.clear()
        thinking_event.clear()
        # intent_queue.task_done()
