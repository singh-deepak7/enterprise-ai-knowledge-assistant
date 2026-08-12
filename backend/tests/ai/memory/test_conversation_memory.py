from app.ai.memory.conversation_memory import ConversationMemory


def test_add_and_get_history():
    memory = ConversationMemory()

    memory.add_user_message("session1", "Hello")
    memory.add_assistant_message("session1", "Hi!")

    history = memory.get_history("session1")

    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi!"


def test_history_limit():
    memory = ConversationMemory(max_history=2)

    memory.add_user_message("s", "1")
    memory.add_user_message("s", "2")
    memory.add_user_message("s", "3")

    history = memory.get_history("s")

    assert len(history) == 2
    assert history[0].content == "2"
    assert history[1].content == "3"


def test_clear_history():
    memory = ConversationMemory()

    memory.add_user_message("s", "hello")
    memory.clear("s")

    assert memory.get_history("s") == []


def test_sessions_are_isolated():
    memory = ConversationMemory()

    memory.add_user_message("a", "hello")
    memory.add_user_message("b", "world")

    assert len(memory.get_history("a")) == 1
    assert len(memory.get_history("b")) == 1
    assert memory.get_history("a")[0].content == "hello"
    assert memory.get_history("b")[0].content == "world"