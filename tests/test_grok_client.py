from src.clients.grok_client import extract_json_object, extract_text_from_response


def test_extract_text_from_response_reads_message_blocks() -> None:
    payload = {
        "output": [
            {"type": "custom_tool_call", "name": "x_keyword_search"},
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"headline":"AI","overview":"ok","items":[]}',
                    }
                ],
            },
        ]
    }

    assert extract_text_from_response(payload) == '{"headline":"AI","overview":"ok","items":[]}'


def test_extract_json_object_handles_code_fence() -> None:
    text = '```json\n{"headline":"AI","overview":"ok","items":[]}\n```'

    assert extract_json_object(text)["headline"] == "AI"
