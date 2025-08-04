"""Streamlit interface for visualizing chat data.

This module provides a web-based interface using Streamlit to explore and visualize
mental health conversation data from the dataset. Users can select conversations
from a dropdown and view the message exchange in a chat-like format.

Features:
- Load conversations from CSV data
- Select conversations by ID from a dropdown
- Display messages in chronological order with role-based styling
- Show conversation metadata and statistics
- Self-contained interface with all dependencies included

Usage:
    Run with: streamlit run aicb/interface.py
"""

from datetime import datetime
from pathlib import Path

import streamlit as st

# Import the data models and reader
from aicb.data_prep.awel_reader import AwelReader
from aicb.data_prep.models import Conversation, Message


def load_data() -> tuple[AwelReader, list[Conversation]]:
    """Load conversation data using the AwelReader.

    Returns:
        tuple: (AwelReader instance, list of conversations)
    """
    # Default data path - can be modified as needed
    data_path = "data/2023_originalfile_nonicknames.csv"

    if not Path(data_path).exists():
        st.error(f"Data file not found: {data_path}")
        st.info("Please ensure the data file exists in the correct location.")
        raise FileNotFoundError(f"Data file not found: {data_path}")

    try:
        reader = AwelReader(data_path, validate_data=False)
        conversations = reader.load_conversations()
        return reader, conversations
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {str(e)}") from e


def format_message_time(timestamp: datetime) -> str:
    """Format message timestamp for display.

    Args:
        timestamp: Message timestamp

    Returns:
        Formatted time string
    """
    return timestamp.strftime("%H:%M")


def display_message(message: Message):
    """Display a single message with appropriate styling.

    Args:
        message: Message object to display
        is_operator: Whether this is an operator message (for styling)
    """
    is_operator = message.role == "operator"

    # Create columns for message layout
    if is_operator:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown(
                f"""
                <div style="
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                    border-left: 4px solid #2196f3;
                    color: #1a1a1a;
                ">
                    <strong style="color: #1565c0;">🎧 Operator</strong> <small style="color: #666;">({format_message_time(message.timestamp)})</small><br>
                    <span style="color: #1a1a1a;">{message.content}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown(
                f"""
                <div style="
                    background-color: #f3e5f5;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 5px 0;
                    border-left: 4px solid #9c27b0;
                    color: #1a1a1a;
                ">
                    <strong style="color: #7b1fa2;">👤 User</strong> <small style="color: #666;">({format_message_time(message.timestamp)})</small><br>
                    <span style="color: #1a1a1a;">{message.content}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def display_conversation_info(conversation: Conversation):
    """Display conversation metadata and information.

    Args:
        conversation: Conversation object to display info for
    """
    st.subheader("📋 Conversation Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Messages", len(conversation.messages))

    with col2:
        st.metric("Topic", conversation.topic)

    with col3:
        duration = "N/A"
        if len(conversation.messages) >= 2:
            start_time = conversation.messages[0].timestamp
            end_time = conversation.messages[-1].timestamp
            duration_minutes = (end_time - start_time).total_seconds() / 60
            duration = f"{duration_minutes:.1f} min"
        st.metric("Duration", duration)

    # Additional details in an expander
    with st.expander("📊 Additional Information"):
        st.write(f"**Conversation ID:** `{conversation.id}`")
        st.write(f"**Start Time:** {conversation.metadata.timestamp.strftime('%d.%m.%Y %H:%M')}")
        st.write(f"**Source:** {conversation.metadata.source}")

        # Message breakdown
        user_messages = sum(1 for msg in conversation.messages if msg.role == "user")
        operator_messages = sum(1 for msg in conversation.messages if msg.role == "operator")
        st.write(f"**User Messages:** {user_messages}")
        st.write(f"**Operator Messages:** {operator_messages}")


def display_dataset_statistics(reader: AwelReader):
    """Display overall dataset statistics.

    Args:
        reader: AwelReader instance with loaded data
    """
    stats = reader.get_statistics()

    if not stats:
        st.warning("No statistics available")
        return

    st.subheader("📈 Dataset Statistics")

    # Display metrics in a vertical layout for better readability in sidebar
    st.metric("Total Conversations", stats.get("total_conversations", 0))  # type:ignore
    st.metric("Total Messages", stats.get("total_messages", 0))  # type: ignore
    st.metric("Avg Messages/Conv", stats.get("avg_messages_per_conversation", 0))  # type: ignore
    st.metric("Avg Duration", f"{stats.get('avg_conversation_length_minutes', 0)} min")  # type: ignore

    # Topics information
    topics = stats.get("topics", [])
    if topics:
        st.write(f"**Available Topics ({len(topics)}):** {', '.join(topics)}")  # type: ignore


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Chat Data Visualizer", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

    st.title("💬 Chat Data Visualizer")
    st.markdown("---")

    # Load data
    with st.spinner("Loading conversation data..."):
        reader, conversations = load_data()

    if not conversations:
        st.stop()

    st.success(f"✅ Loaded {len(conversations)} conversations successfully!")

    # Sidebar for dataset statistics
    with st.sidebar:
        st.header("📊 Dataset Overview")
        display_dataset_statistics(reader)

    # Main content area
    st.header("🔍 Conversation Explorer")

    # Create conversation selection dropdown
    conversation_options = {}
    for conv in conversations:
        # Create a readable label for each conversation
        start_time = conv.metadata.timestamp.strftime("%d.%m.%Y %H:%M")
        message_count = len(conv.messages)
        label = f"{start_time} - {message_count} messages - {conv.topic}"
        conversation_options[label] = conv.id

    selected_label = st.selectbox(
        "Select a conversation to view:",
        options=list(conversation_options.keys()),
        help="Choose a conversation from the dropdown to view its messages",
    )

    if selected_label:
        selected_id = conversation_options[selected_label]
        selected_conversation = reader.get_conversation_by_id(selected_id)

        if selected_conversation:
            # Display conversation information
            display_conversation_info(selected_conversation)

            st.markdown("---")

            # Display messages
            st.subheader("💬 Conversation Messages")

            if not selected_conversation.messages:
                st.info("No messages found in this conversation.")
            else:
                # Sort messages by timestamp to ensure chronological order
                sorted_messages = sorted(selected_conversation.messages, key=lambda x: x.timestamp)

                for message in sorted_messages:
                    display_message(message)

                # Add some spacing at the bottom
                st.markdown("<br><br>", unsafe_allow_html=True)
        else:
            st.error("Selected conversation not found.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em;">
            Chat Data Visualizer | Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
