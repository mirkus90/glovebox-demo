/// <reference types="vite/client" />
interface ImportMetaEnv {
    readonly VITE_KEYWORD_ACTIVATION: string; // the activation keyword for the app
    readonly VITE_TURN_DETECTION_TYPE: TurnDetectionMode; // the mode of turn detection
    readonly VITE_TURN_DETECTION_THRESHOLD: number; // the activation threshold for turn detection
    readonly VITE_TURN_DETECTION_PREFIX_PADDING_MS: number; // the duration of speech audio (in milliseconds) to include before the start of detected speech.
    readonly VITE_TURN_DETECTION_SILENCE_DURATION_MS: number; // the duration of silence (in milliseconds) to detect the end of speech.
    readonly VITE_TURN_DETECTION_INTERRUPT_RESPONSE: string; // whether to interrupt the response when a new turn is detected
    readonly VITE_TURN_DETECTION_EAGERNESS: TurnDetectionEagerness; // the eagerness of the turn detection
}

enum TurnDetectionType {
    server_vad = "server_vad",
    semantic_vad = "semantic_vad",
    none = "none"
}

enum TurnDetectionEagerness {
    auto = "auto",
    low = "low",
    medium = "medium",
    high = "high"
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
