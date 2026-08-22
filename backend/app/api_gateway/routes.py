from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.orchestrator.orchestrator import Orchestrator
from app.stt import FasterWhisperService
from app.tts import VoiceManager


router = APIRouter(
    prefix="/api/v1",
    tags=["API Gateway"],
)


# ==================================================
# SERVICES
# ==================================================

orchestrator = Orchestrator()

# Le modèle STT est chargé une seule fois
stt_service = FasterWhisperService(
    model_size="small",
    device="cpu",
    compute_type="int8",
)

# Les voix TTS sont chargées une seule fois
voice_manager = VoiceManager(
    voices_directory="voices"
)


# ==================================================
# HEALTH
# ==================================================

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "airport-ai-assistant",
        "version": "v1",
        "tts_languages": voice_manager.available_languages(),
    }


# ==================================================
# TEXT CONVERSATION
# ==================================================

@router.post("/conversation")
async def conversation(
    text: str,
    conversation_id: str | None = None,
):
    result = await orchestrator.process(
        text=text,
        conversation_id=conversation_id,
    )

    return result


# ==================================================
# AUDIO CONVERSATION
# ==================================================

@router.post("/conversation/audio")
async def conversation_audio(
    audio: UploadFile = File(...),
    conversation_id: str | None = Form(default=None),
):
    """
    Complete voice pipeline:

        Audio
          ↓
        STT
          ↓
        Orchestrator
          ↓
        LLM
          ↓
        TTS
          ↓
        WAV
    """

    # ==================================================
    # 1. VERIFY AUDIO
    # ==================================================

    if not audio.filename:
        return {
            "status": "error",
            "message": "No audio file provided.",
        }

    audio_bytes = await audio.read()

    if not audio_bytes:
        return {
            "status": "error",
            "message": "The audio file is empty.",
        }

    # ==================================================
    # 2. CREATE TEMPORARY INPUT AUDIO
    # ==================================================

    suffix = Path(
        audio.filename
    ).suffix or ".wav"

    input_temp_path = None
    output_temp_path = None

    try:

        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(audio_bytes)

            input_temp_path = temp_file.name

        print()
        print("=" * 60)
        print("VOICE REQUEST")
        print("=" * 60)

        print(
            f"[API] Audio received: "
            f"{audio.filename}"
        )

        print(
            f"[API] Audio size: "
            f"{len(audio_bytes)} bytes"
        )

        # ==================================================
        # 3. STT
        # ==================================================

        print("[API] Starting STT...")

        text = stt_service.transcribe(
            input_temp_path
        )

        print(
            f"[API] Transcription: {text}"
        )

        if not text.strip():

            return {
                "status": "error",
                "message": "No speech detected.",
            }

        # ==================================================
        # 4. ORCHESTRATOR
        # ==================================================

        print(
            "[API] Sending transcription "
            "to orchestrator..."
        )

        result = await orchestrator.process(
            text=text,
            conversation_id=conversation_id,
        )

        # ==================================================
        # 5. EXTRACT RESPONSE
        # ==================================================

        response_text = result.get(
            "response",
            "",
        )

        if not response_text:

            return {
                "status": "error",
                "message": "The assistant returned an empty response.",
                "transcription": text,
                "conversation": result,
            }

        # ==================================================
        # 6. GET DETECTED LANGUAGE
        # ==================================================

        language_result = result.get(
            "language",
            {},
        )

        language = language_result.get(
            "primary_language",
            "en",
        )

        print(
            f"[API] TTS language: {language}"
        )

        # ==================================================
        # 7. TTS
        # ==================================================

        if not voice_manager.has_voice(language):

            print(
                f"[TTS] No voice available "
                f"for language: {language}"
            )

            # Fallback to English
            language = "en"

        output_file = NamedTemporaryFile(
            delete=False,
            suffix=".wav",
        )

        output_temp_path = output_file.name

        output_file.close()

        print(
            "[API] Starting TTS..."
        )

        voice_manager.synthesize(
            text=response_text,
            language=language,
            output_path=output_temp_path,
        )

        print(
            f"[API] TTS audio generated: "
            f"{output_temp_path}"
        )

        print("=" * 60)
        print()

        # ==================================================
        # 8. RETURN AUDIO
        # ==================================================

        return FileResponse(
            path=output_temp_path,
            media_type="audio/wav",
            filename="assistant_response.wav",
            headers={
                "X-Conversation-Id": result[
                    "conversation_id"
                ],
                "X-Transcription": text,
                "X-Language": language,
            },
        )

    except Exception as error:

        print(
            f"[API] Voice pipeline error: "
            f"{error}"
        )

        return {
            "status": "error",
            "message": str(error),
        }

    finally:

        # ==================================================
        # 9. CLEAN INPUT TEMPORARY FILE
        # ==================================================

        if input_temp_path:

            try:
                Path(
                    input_temp_path
                ).unlink(
                    missing_ok=True
                )

            except Exception as error:

                print(
                    f"[API] Could not delete "
                    f"input temporary file: "
                    f"{error}"
                )