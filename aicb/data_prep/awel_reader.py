"""AWEL dataset reader for mental health conversation data."""

import json
import logging
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from .models import Conversation, Message, Metadata, CandidateAnswers


logger = logging.getLogger(__name__)


class AWELReader:
    """Reader for AWEL mental health conversation dataset.

    Handles loading and parsing conversation data from various formats (JSON, JSONL)
    and converts them to structured Pydantic models for further processing.
    """

    def __init__(self, data_path: Union[str, Path], validate_data: bool = True):
        """Initialize the AWEL reader.

        Args:
            data_path: Path to the dataset file or directory
            validate_data: Whether to validate data against Pydantic models
        """
        self.data_path = Path(data_path)
        self.validate_data = validate_data
        self._conversations: Optional[List[Conversation]] = None

        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {self.data_path}")

    def load_conversations(self) -> List[Conversation]:
        """Load all conversations from the dataset.

        Returns:
            List of Conversation objects

        Raises:
            ValueError: If data format is invalid
            FileNotFoundError: If data files are missing
        """
        if self._conversations is not None:
            return self._conversations

        logger.info(f"Loading conversations from {self.data_path}")

        if self.data_path.is_file():
            self._conversations = self._load_from_file(self.data_path)
        elif self.data_path.is_dir():
            self._conversations = self._load_from_directory(self.data_path)
        else:
            raise ValueError(f"Invalid data path: {self.data_path}")

        logger.info(f"Loaded {len(self._conversations)} conversations")
        return self._conversations

    def _load_from_file(self, file_path: Path) -> List[Conversation]:
        """Load conversations from a single file.

        Args:
            file_path: Path to the data file

        Returns:
            List of Conversation objects
        """
        conversations = []

        if file_path.suffix == ".jsonl":
            conversations = self._load_jsonl(file_path)
        elif file_path.suffix == ".json":
            conversations = self._load_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        return conversations

    def _load_from_directory(self, dir_path: Path) -> List[Conversation]:
        """Load conversations from multiple files in a directory.

        Args:
            dir_path: Path to the directory containing data files

        Returns:
            List of Conversation objects
        """
        conversations = []

        # Look for JSON and JSONL files
        for pattern in ["*.json", "*.jsonl"]:
            for file_path in dir_path.glob(pattern):
                logger.debug(f"Loading from {file_path}")
                conversations.extend(self._load_from_file(file_path))

        return conversations

    def _load_jsonl(self, file_path: Path) -> List[Conversation]:
        """Load conversations from JSONL format.

        Args:
            file_path: Path to JSONL file

        Returns:
            List of Conversation objects
        """
        conversations = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    conversation = self._parse_conversation_data(data)
                    conversations.append(conversation)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON on line {line_num} in {file_path}: {e}")
                    if self.validate_data:
                        raise
                except Exception as e:
                    logger.error(f"Error parsing conversation on line {line_num}: {e}")
                    if self.validate_data:
                        raise

        return conversations

    def _load_json(self, file_path: Path) -> List[Conversation]:
        """Load conversations from JSON format.

        Args:
            file_path: Path to JSON file

        Returns:
            List of Conversation objects
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conversations = []

        # Handle both single conversation and list of conversations
        if isinstance(data, list):
            for item in data:
                conversation = self._parse_conversation_data(item)
                conversations.append(conversation)
        else:
            conversation = self._parse_conversation_data(data)
            conversations.append(conversation)

        return conversations

    def _parse_conversation_data(self, data: Dict) -> Conversation:
        """Parse raw conversation data into a Conversation object.

        Args:
            data: Raw conversation data dictionary

        Returns:
            Conversation object

        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Handle different data formats from requirements.md vs data-model.md
            if "user_message" in data and "expert_response" in data:
                # Format from requirements.md - single user/expert exchange
                conversation = self._parse_simple_format(data)
            else:
                # Format from data-model.md - full conversation with messages
                conversation = Conversation(**data)

            return conversation

        except Exception as e:
            logger.error(f"Failed to parse conversation data: {e}")
            logger.debug(f"Raw data: {data}")
            raise ValueError(f"Invalid conversation data: {e}")

    def _parse_simple_format(self, data: Dict) -> Conversation:
        """Parse simple user_message/expert_response format into full conversation.

        Args:
            data: Data in simple format from requirements.md

        Returns:
            Conversation object
        """
        # Convert simple format to full conversation format
        messages = [
            Message(timestamp=data["metadata"]["timestamp"], role="user", content=data["user_message"]),
            Message(timestamp=data["metadata"]["timestamp"], role="expert", content=data["expert_response"]),
        ]

        metadata = Metadata(**data["metadata"])

        return Conversation(id=data["id"], topic=data["topic"], messages=messages, metadata=metadata)

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID.

        Args:
            conversation_id: The conversation ID to search for

        Returns:
            Conversation object if found, None otherwise
        """
        conversations = self.load_conversations()

        for conversation in conversations:
            if conversation.id == conversation_id:
                return conversation

        return None

    def filter_by_topic(self, topic: str) -> List[Conversation]:
        """Filter conversations by topic.

        Args:
            topic: Topic to filter by

        Returns:
            List of conversations matching the topic
        """
        conversations = self.load_conversations()
        return [conv for conv in conversations if conv.topic == topic]

    def get_topics(self) -> List[str]:
        """Get all unique topics in the dataset.

        Returns:
            List of unique topic strings
        """
        conversations = self.load_conversations()
        topics = set(conv.topic for conv in conversations)
        return sorted(list(topics))

    def get_statistics(self) -> Dict[str, Union[int, float, Dict]]:
        """Get dataset statistics.

        Returns:
            Dictionary containing dataset statistics
        """
        conversations = self.load_conversations()

        if not conversations:
            return {}

        total_conversations = len(conversations)
        total_messages = sum(len(conv.messages) for conv in conversations)
        topics = self.get_topics()

        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = len(self.filter_by_topic(topic))

        avg_messages_per_conversation = total_messages / total_conversations

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "unique_topics": len(topics),
            "topics": topics,
            "topic_distribution": topic_counts,
            "avg_messages_per_conversation": round(avg_messages_per_conversation, 2),
        }

    def iterate_conversations(self) -> Iterator[Conversation]:
        """Iterate over conversations without loading all into memory.

        Yields:
            Conversation objects one at a time
        """
        # For large datasets, this could be optimized to stream data
        # For now, we load all and iterate
        conversations = self.load_conversations()
        for conversation in conversations:
            yield conversation

    def export_conversations(self, output_path: Union[str, Path], format: str = "jsonl") -> None:
        """Export conversations to a file.

        Args:
            output_path: Path to save the exported data
            format: Export format ('json' or 'jsonl')
        """
        conversations = self.load_conversations()
        output_path = Path(output_path)

        if format == "jsonl":
            with open(output_path, "w", encoding="utf-8") as f:
                for conv in conversations:
                    f.write(conv.model_dump_json() + "\n")
        elif format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                data = [conv.model_dump() for conv in conversations]
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        logger.info(f"Exported {len(conversations)} conversations to {output_path}")


class CandidateAnswersReader:
    """Reader for candidate answers generated by different models."""

    def __init__(self, data_path: Union[str, Path]):
        """Initialize the candidate answers reader.

        Args:
            data_path: Path to the candidate answers file or directory
        """
        self.data_path = Path(data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {self.data_path}")

    def load_candidate_answers(self) -> List[CandidateAnswers]:
        """Load all candidate answers.

        Returns:
            List of CandidateAnswers objects
        """
        if self.data_path.is_file():
            return self._load_from_file(self.data_path)
        elif self.data_path.is_dir():
            return self._load_from_directory(self.data_path)
        else:
            raise ValueError(f"Invalid data path: {self.data_path}")

    def _load_from_file(self, file_path: Path) -> List[CandidateAnswers]:
        """Load candidate answers from a single file."""
        candidates = []

        if file_path.suffix == ".jsonl":
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        candidates.append(CandidateAnswers(**data))
        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        candidates.append(CandidateAnswers(**item))
                else:
                    candidates.append(CandidateAnswers(**data))

        return candidates

    def _load_from_directory(self, dir_path: Path) -> List[CandidateAnswers]:
        """Load candidate answers from multiple files in a directory."""
        candidates = []

        for pattern in ["*.json", "*.jsonl"]:
            for file_path in dir_path.glob(pattern):
                candidates.extend(self._load_from_file(file_path))

        return candidates

    def get_candidate_by_id(self, conversation_id: str) -> Optional[CandidateAnswers]:
        """Get candidate answers for a specific conversation ID."""
        candidates = self.load_candidate_answers()

        for candidate in candidates:
            if candidate.id == conversation_id:
                return candidate

        return None
