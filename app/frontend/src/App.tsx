import { useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import StatusMessage from "@/components/ui/status-message";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";
import useSTT from "@/hooks/useSTT";

import { GroundingFile, ToolResult } from "./types";

import logo from "./assets/glovebox.png";
import activationTone from "./assets/activation_tone.mp3";
import deactivationTone from "./assets/deactivation_tone.mp3";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [appActive, setAppActive] = useState(false);
    const [isActivationDetecting, setIsActivationDetecting] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        enableInputAudioTranscription: true,
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            stopAudioPlayer();
        },
        onReceivedExtensionMiddleTierToolResponse: message => {
            const result: ToolResult = JSON.parse(message.tool_result);

            const files: GroundingFile[] = result.sources.map(x => {
                return { id: x.chunk_id, name: x.title, content: x.chunk };
            });

            setGroundingFiles(prev => [...prev, ...files]);
            setSelectedFile(files[0]);
        },
        onReceivedInputAudioBufferCleared: async () => {
            // deactivation keyword management
            // first, stop the audio player, so that you don't hear the audio when the conversation is stopped
            stopAudioPlayer();
            await stopAudioRecording();

            // play the deactivation tone
            playMp3File(deactivationTone);

            // when stopping the conversation with the AI, start again the recognition of keyword
            await startKeywordRecognition();
            setIsActivationDetecting(true);
            setIsRecording(false);
            // clear the selected file. This is to avoid showing the content of the file when the user stops the conversation
            setSelectedFile(null);
            // clear the grounding files
            setGroundingFiles([]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer, playMp3File: playMp3File } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const {
        start: startKeywordRecognition,
        reset: resetKeywordRecognition,
        stop: stopKeywordRecognition
    } = useSTT({
        // when the activation keyword is detected, we stop the keyword recognition and start the conversation with the AI
        onKeywordDetected: () => {
            setIsActivationDetecting(false);
            onToggleListening();
        }
    });

    const onToggleListening = async () => {
        if (!isRecording) {
            // when starting the conversation with the AI, we stop the keyword recognition and start the audio recording
            // this is to manage the user clicking on the microphone icon to start the conversation
            if (isActivationDetecting) {
                await stopKeywordRecognition();
                setIsActivationDetecting(false);
            }
            startSession();
            await startAudioRecording();
            resetAudioPlayer();

            setIsRecording(true);

            // play the activation tone
            playMp3File(activationTone);
        } else {
            // stop the reproduction of the current AI audio sample
            stopAudioPlayer();

            await stopAudioRecording();
            // send the command to clear the audio buffer
            inputAudioBufferClear();

            // when stopping the conversation with the AI, start again the recognition of keyword
            await startKeywordRecognition();
            setIsActivationDetecting(true);
            setIsRecording(false);

            // clear the selected file. This is to avoid showing the content of the file when the user stops the conversation
            setSelectedFile(null);

            // clear the grounding files
            setGroundingFiles([]);
        }
    };

    const onStartAppButtonClick = async () => {
        if (!appActive) {
            await resetKeywordRecognition();
            await startKeywordRecognition();
            setAppActive(true);
            setIsActivationDetecting(true);
        } else {
            // stop the keyword recognition and, if active, the conversation with the AI
            await stopKeywordRecognition();
            if (isRecording) {
                onToggleListening();
            }
            setAppActive(false);
            setIsActivationDetecting(false);
        }
    };

    const { t } = useTranslation();

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <div className="p-4 sm:absolute sm:left-4 sm:top-4">
                <Button onClick={onStartAppButtonClick} className={`h-12 w-60 ${!appActive ? "bg-blue-600 hover:bg-blue-700" : "bg-red-600 hover:bg-red-700"}`}>
                    {!appActive ? t("app.start") : t("app.stop")}
                </Button>
            </div>
            <main className="flex flex-grow flex-col items-center justify-center">
                <img src={logo} alt="Logo" className="h-32 w-32 flex-col items-center justify-center" />
                <h1 className="mb-8 bg-gradient-to-r from-blue-600 to-blue-600 bg-clip-text text-4xl font-bold text-transparent md:text-7xl">
                    {t("app.title")}
                </h1>
                <div className="mb-4 flex flex-col items-center justify-center">
                    <Button
                        disabled={!appActive}
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}`}
                        aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                {t("app.stopConversation")}
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                            </>
                        )}
                    </Button>
                    <StatusMessage isRecording={isRecording} />
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
            </main>

            <footer className="py-4 text-center">
                <p>{t("app.footer")}</p>
            </footer>

            {/* <div className="flex-grow overflow-hidden">
                <pre className="h-[40vh] overflow-auto text-wrap rounded-md bg-gray-100 p-4 text-sm">
                    <code>{selectedFile?.content}</code>
                </pre>
            </div> */}
            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
