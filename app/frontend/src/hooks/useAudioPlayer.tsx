import { useRef } from "react";

import { Player } from "@/components/audio/player";

const SAMPLE_RATE = 24000;

export default function useAudioPlayer() {
    const audioPlayer = useRef<Player>();

    const reset = () => {
        audioPlayer.current = new Player();
        audioPlayer.current.init(SAMPLE_RATE);
    };

    const play = (base64Audio: string) => {
        const binary = atob(base64Audio);
        const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
        const pcmData = new Int16Array(bytes.buffer);

        audioPlayer.current?.play(pcmData);
    };

    const playMp3File = async (filePath: string) => {
        const response = await fetch(filePath);
        const mp3Bytes = new Uint8Array(await response.arrayBuffer());
        const audioCtx = new AudioContext();
        const decoded = await audioCtx.decodeAudioData(mp3Bytes.buffer);

        // Use the first channel for simplicity
        const inputData = (await decoded).getChannelData(0);
        const originalRate = (await decoded).sampleRate;

        // If the file's sample rate differs, do a quick naive resample
        let floatData = inputData;
        if (originalRate !== SAMPLE_RATE) {
            const ratio = SAMPLE_RATE / originalRate;
            const newLen = Math.floor(floatData.length * ratio);
            const resampled = new Float32Array(newLen);
            for (let i = 0; i < newLen; i++) {
                resampled[i] = floatData[Math.floor(i / ratio)];
            }
            floatData = resampled;
        }

        // Convert float samples [-1..1] to Int16
        const pcmData = new Int16Array(floatData.length);
        for (let i = 0; i < floatData.length; i++) {
            const s = Math.max(-1, Math.min(1, floatData[i]));
            pcmData[i] = s < 0 ? s * 32768 : s * 32767;
        }

        audioPlayer.current?.play(pcmData);
    };

    const stop = () => {
        audioPlayer.current?.stop();
    };

    return { reset, play, stop, playMp3File };
}
