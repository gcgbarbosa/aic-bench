"""AWEL dataset reader for mental health conversation data.

This module provides readers for the AWEL (Awel) mental health conversation dataset.
The dataset contains conversations between users and mental health operators, stored
in CSV format with conversation text in the 'gesprek anoniem' column.

The conversation text follows this format:
    Date/time: DD.MM.YYYY, HH:MM - HH:MM

    HH:MM Sender: Message content
    HH:MM Sender: Message content
    ...

Example conversation text:
    Date/time: 10.02.2023, 17:22 - 17:43

    17:22 Awel wachtrij: Hallo!
    17:26 *****: er is al een een week ruzie...
    17:31 Awel: Dag *****, welkom bij awel!

Classes:
    AwelReader: Main reader class for parsing AWEL CSV data into structured conversations

Example usage:
    >>> reader = AwelReader("data/2023_originalfile_nonicknames.csv")
    >>> conversations = reader.load_conversations()
    >>> stats = reader.get_statistics()
    >>> print(f"Loaded {stats['total_conversations']} conversations")
"""

from pathlib import Path

from .models import Conversation, Message, Metadata

import pandas as pd

from loguru import logger
import re
import uuid
from datetime import datetime


class AwelReader:
    """Reader for AWEL mental health conversation dataset.

    This class handles loading and parsing conversation data from CSV files containing
    AWEL mental health chat conversations. It converts raw conversation text into
    structured Pydantic models for further processing and analysis.

    The reader parses conversations that follow the AWEL chat format:
    - Date/time header with conversation timestamp
    - Individual messages with timestamps, sender names, and content
    - Special handling for operator roles (Awel, Awel wachtrij) vs users

    Attributes:
        data_path (Path): Path to the CSV file containing conversation data
        validate_data (bool): Whether to validate parsed data against Pydantic models
        _conversations (List[Conversation]): Cached list of parsed conversations

    Example:
        >>> reader = AwelReader("data/conversations.csv")
        >>> conversations = reader.load_conversations()
        >>> print(f"Loaded {len(conversations)} conversations")
        >>> topics = reader.get_topics()
        >>> stats = reader.get_statistics()
    """

    def __init__(self, data_path: str, validate_data: bool = True):
        """Initialize the AWEL reader.

        Args:
            data_path (str): Path to the CSV file containing AWEL conversation data.
                Should point to a file like '2023_originalfile_nonicknames.csv'
            validate_data (bool, optional): Whether to validate parsed data against
                Pydantic models. If True, invalid data will raise exceptions.
                If False, invalid conversations will be logged and skipped.
                Defaults to True.

        Raises:
            FileNotFoundError: If the specified data_path does not exist

        Example:
            >>> reader = AwelReader("data/2023_originalfile_nonicknames.csv")
            >>> reader = AwelReader("data/conversations.csv", validate_data=False)
        """
        self.data_path = Path(data_path)
        self.validate_data = validate_data
        self._conversations: list[Conversation] = []

        logger.info(f"Initializing AwelReader with data path: {self.data_path}")

        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {self.data_path}")

    def load_conversations(self) -> list[Conversation]:
        """Load all conversations from the CSV dataset.

        Reads the CSV file and parses each row in the 'gesprek anoniem' column
        into structured Conversation objects. The method caches results, so
        subsequent calls return the same data without re-parsing.

        Returns:
            list[Conversation]: List of parsed Conversation objects, each containing
                structured message data, metadata, and conversation details.

        Raises:
            ValueError: If the CSV format is invalid or 'gesprek anoniem' column
                is missing
            FileNotFoundError: If the CSV file specified in data_path doesn't exist
            pd.errors.EmptyDataError: If the CSV file is empty

        Example:
            >>> reader = AwelReader("data/conversations.csv")
            >>> conversations = reader.load_conversations()
            >>> print(f"Loaded {len(conversations)} conversations")
            >>> first_conv = conversations[0]
            >>> print(f"First conversation has {len(first_conv.messages)} messages")
        """

        logger.info(f"Loading conversations from {self.data_path}")
        data = pd.read_csv(self.data_path)

        chat_column = data["gesprek anoniem"]

        if type(chat_column) is not pd.Series:
            raise ValueError("Expected 'gesprek anoniem' column to be a pandas Series")

        self._conversations = self._parse_conversation_list(chat_column)

        logger.info(f"Loaded {len(self._conversations)} conversations")
        return self._conversations

    def _parse_conversation(self, text: str, source: str = "awel_chat") -> Conversation:
        """Parse a single conversation text into a structured Conversation object.

        This method extracts the conversation timestamp, parses individual messages
        with their timestamps and roles, and creates a structured Conversation object.

        The expected text format is:
            Date/time: DD.MM.YYYY, HH:MM - HH:MM

            HH:MM Sender: Message content
            HH:MM Sender: Message content
            ...

        Args:
            text (str): Raw conversation text from the 'gesprek anoniem' column
            source (str, optional): Source identifier for the conversation metadata.
                Defaults to "awel_chat".

        Returns:
            Conversation: Structured conversation object with parsed messages,
                metadata, and unique ID.

        Raises:
            ValueError: If the conversation timestamp cannot be extracted or
                if the text format is invalid

        Example:
            >>> text = "Date/time: 10.02.2023, 17:22 - 17:43\\n\\n17:22 Awel: Hello!"
            >>> conv = reader._parse_conversation(text)
            >>> print(f"Conversation ID: {conv.id}")
            >>> print(f"Messages: {len(conv.messages)}")
        """
        # Extract conversation-level timestamp
        conv_date_match = re.search(r"Date/time:\s*([\d.]+),\s*(\d{2}:\d{2})", text)
        if not conv_date_match:
            raise ValueError("Could not find conversation start time")

        conv_date = conv_date_match.group(1)
        conv_time = conv_date_match.group(2)
        conv_datetime = datetime.strptime(f"{conv_date} {conv_time}", "%d.%m.%Y %H:%M")

        # Regex for messages: captures HH:MM, sender, and message
        msg_pattern = re.compile(r"(\d{2}:\d{2})\s+([^:]+):\s+([^\n]+(?:\n(?!\d{2}:\d{2}).*)*)")
        messages = []
        for match in msg_pattern.finditer(text):
            time_str, role, content = match.groups()
            msg_datetime = datetime.strptime(f"{conv_date} {time_str}", "%d.%m.%Y %H:%M")

            messages.append(
                Message(
                    datetime=msg_datetime,
                    role="operator" if role.strip() in ["Awel", "Awel wachtrij"] else "user",
                    content=content.strip(),
                )
            )

        # Build Conversation
        return Conversation(
            id=str(uuid.uuid4()),
            topic="Conflict with friends",
            messages=messages,
            metadata=Metadata(timestamp=conv_datetime, source=source),
            raw=text,
        )

    def _parse_conversation_list(self, data: pd.Series) -> list[Conversation]:
        """Parse a pandas Series of conversation texts into Conversation objects.

        Iterates through each conversation text in the Series and attempts to parse
        it into a structured Conversation object. Failed parses are logged and
        optionally skipped based on the validate_data setting.

        Args:
            data (pd.Series): Series containing raw conversation texts from the
                'gesprek anoniem' column of the CSV file.

        Returns:
            list[Conversation]: List of successfully parsed Conversation objects.
                May be shorter than input if some conversations failed to parse
                and validate_data=False.

        Raises:
            ValueError: If validate_data=True and any conversation fails to parse

        Example:
            >>> series = pd.Series(["Date/time: 10.02.2023...", "Date/time: 11.02.2023..."])
            >>> conversations = reader._parse_conversation_list(series)
            >>> print(f"Parsed {len(conversations)} conversations")
        """
        conversations = []

        for idx, row in enumerate(data):
            try:
                convo = self._parse_conversation(row)
                conversations.append(convo)

            except Exception as e:
                logger.error(f"Failed to parse conversation data: {e} with index {idx}")
                # logger.debug(f"Raw data: {data}")
                # raise ValueError(f"Invalid conversation data: {e}")

        return conversations

    def filter_by_topic(self, topic: str) -> list[Conversation]:
        """Filter conversations by topic.

        Args:
            topic (str): Topic string to filter by. Must match exactly.

        Returns:
            list[Conversation]: List of conversations that have the specified topic.

        Example:
            >>> reader = AwelReader("data/conversations.csv")
            >>> anxiety_convs = reader.filter_by_topic("anxiety")
            >>> print(f"Found {len(anxiety_convs)} anxiety conversations")
        """
        conversations = self.load_conversations()
        return [conv for conv in conversations if conv.topic == topic]

    def get_topics(self) -> list[str]:
        """Get all unique topics in the dataset.

        Returns:
            list[str]: Sorted list of unique topic strings found across all conversations.

        Example:
            >>> reader = AwelReader("data/conversations.csv")
            >>> topics = reader.get_topics()
            >>> print(f"Available topics: {topics}")
            >>> print(f"Found {len(topics)} unique topics")
        """
        conversations = self.load_conversations()
        topics = set(conv.topic for conv in conversations)
        return sorted(list(topics))

    def get_conversation_by_id(self, conversation_id: str) -> Conversation | None:
        """Get a specific conversation by its ID.

        Args:
            conversation_id (str): The unique identifier of the conversation to find.

        Returns:
            Conversation | None: The conversation object if found, None otherwise.

        Example:
            >>> reader = AwelReader("data/conversations.csv")
            >>> conv = reader.get_conversation_by_id("some-uuid-here")
            >>> if conv:
            ...     print(f"Found conversation with {len(conv.messages)} messages")
        """
        conversations = self.load_conversations()
        for conversation in conversations:
            if conversation.id == conversation_id:
                return conversation
        return None

    def get_statistics(self) -> dict[str, int | float | list[str]]:
        """Get comprehensive statistics about the dataset.

        Returns:
            dict: Dictionary containing various statistics including:
                - total_conversations: Total number of conversations
                - total_messages: Total number of messages across all conversations
                - avg_messages_per_conversation: Average messages per conversation
                - unique_topics: Number of unique topics
                - topics: List of all unique topics
                - avg_conversation_length: Average conversation duration in minutes

        Example:
            >>> reader = AwelReader("data/conversations.csv")
            >>> stats = reader.get_statistics()
            >>> print(f"Dataset contains {stats['total_conversations']} conversations")
            >>> print(f"Average messages per conversation: {stats['avg_messages_per_conversation']:.1f}")
        """
        conversations = self.load_conversations()

        if not conversations:
            return {}

        total_conversations = len(conversations)
        total_messages = sum(len(conv.messages) for conv in conversations)
        topics = self.get_topics()

        # Calculate average conversation duration
        durations = []
        for conv in conversations:
            if len(conv.messages) >= 2:
                start_time = conv.messages[0].timestamp
                end_time = conv.messages[-1].timestamp
                duration_minutes = (end_time - start_time).total_seconds() / 60
                durations.append(duration_minutes)

        avg_duration = sum(durations) / len(durations) if durations else 0
        avg_messages_per_conversation = total_messages / total_conversations

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages_per_conversation, 2),
            "unique_topics": len(topics),
            "topics": topics,
            "avg_conversation_length_minutes": round(avg_duration, 2),
        }
