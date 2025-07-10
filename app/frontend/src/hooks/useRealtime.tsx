import useWebSocket from "react-use-websocket";

import {
    InputAudioBufferAppendCommand,
    InputAudioBufferClearCommand,
    Message,
    ResponseAudioDelta,
    ResponseAudioTranscriptDelta,
    ResponseDone,
    SessionUpdateCommand,
    ExtensionMiddleTierToolResponse,
    ResponseInputAudioTranscriptionCompleted,
    InputTextCommand
} from "@/types";

type Parameters = {
    useDirectAoaiApi?: boolean; // If true, the middle tier will be skipped and the AOAI ws API will be called directly
    aoaiEndpointOverride?: string;
    aoaiApiKeyOverride?: string;
    aoaiModelOverride?: string;

    enableInputAudioTranscription?: boolean;
    onWebSocketOpen?: () => void;
    onWebSocketClose?: () => void;
    onWebSocketError?: (event: Event) => void;
    onWebSocketMessage?: (event: MessageEvent<any>) => void;

    onReceivedResponseAudioDelta?: (message: ResponseAudioDelta) => void;
    onReceivedInputAudioBufferSpeechStarted?: (message: Message) => void;
    onReceivedResponseDone?: (message: ResponseDone) => void;
    onReceivedExtensionMiddleTierToolResponse?: (message: ExtensionMiddleTierToolResponse) => void;
    onReceivedResponseAudioTranscriptDelta?: (message: ResponseAudioTranscriptDelta) => void;
    onReceivedInputAudioTranscriptionCompleted?: (message: ResponseInputAudioTranscriptionCompleted) => void;
    onReceivedInputAudioBufferCleared?: () => void;
    onReceivedError?: (message: Message) => void;
};

export default function useRealTime({
    useDirectAoaiApi,
    aoaiEndpointOverride,
    aoaiApiKeyOverride,
    aoaiModelOverride,
    enableInputAudioTranscription,
    onWebSocketOpen,
    onWebSocketClose,
    onWebSocketError,
    onWebSocketMessage,
    onReceivedResponseDone,
    onReceivedResponseAudioDelta,
    onReceivedResponseAudioTranscriptDelta,
    onReceivedInputAudioBufferSpeechStarted,
    onReceivedExtensionMiddleTierToolResponse,
    onReceivedInputAudioTranscriptionCompleted,
    onReceivedInputAudioBufferCleared,
    onReceivedError
}: Parameters) {
    const wsEndpoint = useDirectAoaiApi
        ? `${aoaiEndpointOverride}/openai/realtime?api-key=${aoaiApiKeyOverride}&deployment=${aoaiModelOverride}&api-version=2024-10-01-preview`
        : `/realtime`;

    const { sendJsonMessage } = useWebSocket(wsEndpoint, {
        onOpen: () => onWebSocketOpen?.(),
        onClose: () => onWebSocketClose?.(),
        onError: event => onWebSocketError?.(event),
        onMessage: event => onMessageReceived(event),
        shouldReconnect: () => true
    });

    const startSession = () => {
        const command: SessionUpdateCommand = {
            type: "session.update",
            session: {
                turn_detection: {
                    // turn detection configuration
                    type: import.meta.env.VITE_TURN_DETECTION_TYPE as TurnDetectionType,
                    ...(import.meta.env.VITE_TURN_DETECTION_PREFIX_PADDING_MS
                        ? {
                              prefix_padding_ms: Number(import.meta.env.VITE_TURN_DETECTION_PREFIX_PADDING_MS)
                          }
                        : {}),
                    ...(import.meta.env.VITE_TURN_DETECTION_THRESHOLD
                        ? {
                              threshold: parseFloat(String(import.meta.env.VITE_TURN_DETECTION_THRESHOLD))
                          }
                        : {}),
                    ...(import.meta.env.VITE_TURN_DETECTION_SILENCE_DURATION_MS
                        ? {
                              silence_duration_ms: Number(import.meta.env.VITE_TURN_DETECTION_SILENCE_DURATION_MS)
                          }
                        : {}),
                    ...(import.meta.env.VITE_TURN_DETECTION_INTERRUPT_RESPONSE
                        ? {
                              interrupt_response: import.meta.env.VITE_TURN_DETECTION_INTERRUPT_RESPONSE === "true"
                          }
                        : {}),
                    ...(import.meta.env.VITE_TURN_DETECTION_EAGERNESS
                        ? {
                              eagerness: import.meta.env.VITE_TURN_DETECTION_EAGERNESS as TurnDetectionEagerness
                          }
                        : {})
                }
            }
        };

        if (enableInputAudioTranscription) {
            command.session.input_audio_transcription = {
                // use the gpt-4o-transcribe model for audio transcription as it is quicker than whisper-1 and with higher rate limit
                model: "gpt-4o-transcribe"
            };
        }

        sendJsonMessage(command);
    };

    const addUserAudio = (base64Audio: string) => {
        const command: InputAudioBufferAppendCommand = {
            type: "input_audio_buffer.append",
            audio: base64Audio
        };

        sendJsonMessage(command);
    };

    const addUserText = (text: string) => {
        const command: InputTextCommand = {
            type: "input_text",
            text: text
        };

        sendJsonMessage(command);
    };

    const inputAudioBufferClear = () => {
        const command: InputAudioBufferClearCommand = {
            type: "input_audio_buffer.clear"
        };

        sendJsonMessage(command);
    };

    const onMessageReceived = (event: MessageEvent<any>) => {
        onWebSocketMessage?.(event);

        let message: Message;
        try {
            message = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse JSON message:", e);
            throw e;
        }

        switch (message.type) {
            case "response.done":
                onReceivedResponseDone?.(message as ResponseDone);
                break;
            case "response.audio.delta":
                onReceivedResponseAudioDelta?.(message as ResponseAudioDelta);
                break;
            case "response.audio_transcript.delta":
                onReceivedResponseAudioTranscriptDelta?.(message as ResponseAudioTranscriptDelta);
                break;
            case "input_audio_buffer.speech_started":
                onReceivedInputAudioBufferSpeechStarted?.(message);
                break;
            case "conversation.item.input_audio_transcription.completed":
                onReceivedInputAudioTranscriptionCompleted?.(message as ResponseInputAudioTranscriptionCompleted);
                break;
            case "extension.middle_tier_tool_response":
                onReceivedExtensionMiddleTierToolResponse?.(message as ExtensionMiddleTierToolResponse);
                break;
            // handle the case when the input audio buffer is cleared (as effect of the input_audio_buffer.clear command sent by the server on the stop keyword)
            case "input_audio_buffer.cleared":
                onReceivedInputAudioBufferCleared?.();
                break;
            case "error":
                onReceivedError?.(message);
                break;
        }
    };

    return { startSession, addUserAudio, inputAudioBufferClear, addUserText };
}
