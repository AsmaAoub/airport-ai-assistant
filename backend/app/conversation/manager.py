from app.conversation.context import ConversationContext


class ConversationManager:
    """
    Manages conversation state and context.
    """

    def __init__(self):
        self.conversations: dict[str, ConversationContext] = {}

    def get_or_create(
        self,
        conversation_id: str
    ) -> ConversationContext:
        """
        Retrieve an existing conversation or create a new one.
        """

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id
            )

        return self.conversations[conversation_id]

    # ==========================================================
    # LANGUAGE
    # ==========================================================

    def update_language(
        self,
        context: ConversationContext,
        language_result: dict,
    ) -> None:
        """
        Update conversation language information.
        """

        primary_language = language_result.get(
            "primary_language",
            "unknown",
        )

        languages = language_result.get(
            "languages",
            [],
        )

        context.last_language = primary_language

        for language in languages:
            if language not in context.active_languages:
                context.active_languages.append(language)

    # ==========================================================
    # HISTORY
    # ==========================================================

    def add_message(
        self,
        context: ConversationContext,
        role: str,
        content: str,
    ) -> None:
        """
        Add a message to the conversation history.
        """

        context.history.append(
            {
                "role": role,
                "content": content,
            }
        )

    # ==========================================================
    # INTENT
    # ==========================================================

    def update_intent(
        self,
        context: ConversationContext,
        intent: str | None,
    ) -> None:
        """
        Update the current conversation intent.
        """

        if intent is not None and intent != "UNKNOWN":
            context.current_intent = intent

    # ==========================================================
    # ENTITIES
    # ==========================================================

    def update_entities(
        self,
        context: ConversationContext,
        entities: dict,
    ) -> None:
        """
        Update conversation entities.

        New entities are added to the existing context.
        Existing entities are overwritten only when a new
        value is explicitly provided.
        """

        if not entities:
            return

        context.entities.update(entities)

    # ==========================================================
    # CONTEXT
    # ==========================================================

    def get_context_entities(
        self,
        context: ConversationContext,
    ) -> dict:
        """
        Return the entities currently stored in the conversation.
        """

        return context.entities.copy()

    def enrich_entities(
        self,
        context: ConversationContext,
        entities: dict,
    ) -> dict:
        """
        Complete missing entities using the conversation context.

        Example:

        Previous message:
            Where is flight AT123?

        Context:
            flight_number = AT123

        New message:
            And the gate?

        Airport NLP:
            intent = GET_FLIGHT_GATE
            entities = {}

        Result:
            flight_number = AT123
        """

        enriched_entities = context.entities.copy()

        for key, value in entities.items():
            if value is not None:
                enriched_entities[key] = value

        return enriched_entities