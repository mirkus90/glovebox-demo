import { useRef } from "react";
import * as speechsdk from "microsoft-cognitiveservices-speech-sdk";
import axios from "axios";
import Cookie from "universal-cookie";

interface STTParameters {
    onKeywordDetected: () => void;
}

export default function useSTT(params: STTParameters) {
    const { onKeywordDetected } = params;
    const recognizer = useRef<speechsdk.SpeechRecognizer>();

    const reset = async () => {
        const tokenObj = await getTokenOrRefresh();
        const speechConfig = speechsdk.SpeechConfig.fromAuthorizationToken(tokenObj.authToken, tokenObj.region);
        speechConfig.speechRecognitionLanguage = "en-US";

        const audioConfig = speechsdk.AudioConfig.fromDefaultMicrophoneInput();
        recognizer.current = new speechsdk.SpeechRecognizer(speechConfig, audioConfig);
    };

    const start = () => {
        recognizer.current?.startContinuousRecognitionAsync();
    };

    if (recognizer.current) {
        recognizer.current.recognized = (_, event) => {
            console.log(`RECOGNIZED for keyword: Text=${event.result.text}`);
            if (event.result.text.toLowerCase().includes("assistant")) {
                console.log("Keyword detected");
                recognizer.current?.stopContinuousRecognitionAsync();
                onKeywordDetected();
            }
        };
    }

    const stop = () => {
        recognizer.current?.stopContinuousRecognitionAsync();
    };

    async function getTokenOrRefresh() {
        const cookie = new Cookie();
        const speechToken = cookie.get("speech-token");

        if (speechToken === undefined) {
            try {
                const res = await axios.get("/speech/token");
                // You need to include the "aad#" prefix and the "#" (hash) separator between resource ID and Microsoft Entra access token.
                const token = "aad#" + res.data.resource_id + "#" + res.data.token;
                const region = res.data.region;
                cookie.set("speech-token", region + ":" + token, { maxAge: 540, path: "/" });

                console.log("Token fetched from back-end: " + token);
                return { authToken: token, region: region };
            } catch (err: any) {
                console.log(err.response.data);
                return { authToken: null, error: err.response.data };
            }
        } else {
            console.log("Token fetched from cookie: " + speechToken);
            const idx = speechToken.indexOf(":");
            return { authToken: speechToken.slice(idx + 1), region: speechToken.slice(0, idx) };
        }
    }

    return { start, stop, reset };
}
