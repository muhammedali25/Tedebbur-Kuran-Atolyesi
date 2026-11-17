package app.mektubat.okuyucu;

import android.speech.tts.UtteranceProgressListener;

/** Okuma bitince (ya da hata verince) sayfaya haber verir. */
final class TtsListener extends UtteranceProgressListener {
    private final NativeBridge bridge;

    TtsListener(NativeBridge bridge) {
        this.bridge = bridge;
    }

    @Override public void onStart(String id) { }
    @Override public void onDone(String id) { bridge.done(); }
    @Override public void onError(String id) { bridge.done(); }
}
