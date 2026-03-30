import { useTranslation } from 'react-i18next'
import { MicrophoneIcon, StopIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid'
import { useVoice } from '../hooks/useVoice'
import { useUserStore } from '../stores/userStore'
import clsx from 'clsx'

interface VoiceInputProps {
  onTranscript: (text: string) => void
}

export default function VoiceInput({ onTranscript }: VoiceInputProps) {
  const { t } = useTranslation()
  const { lang } = useUserStore()
  const bcp47 = lang === 'ta' ? 'ta-IN' : 'en-IN'
  const { isListening, transcript, error, supported, startListening, stopListening } =
    useVoice(bcp47)

  const handleClick = () => {
    if (isListening) {
      stopListening()
      if (transcript) onTranscript(transcript)
    } else {
      startListening()
    }
  }

  if (!supported) {
    return (
      <div className="flex items-center gap-2 text-slate-500 text-sm">
        <ExclamationCircleIcon className="w-5 h-5" />
        {t('voice_not_supported')}
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        id="voice-btn"
        onClick={handleClick}
        aria-label={isListening ? t('listening') : t('tap_to_speak')}
        aria-pressed={isListening}
        className={clsx(
          'relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg',
          isListening
            ? 'bg-red-500 hover:bg-red-600 scale-110 shadow-red-500/40'
            : 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/30'
        )}
      >
        {/* Pulse rings when listening */}
        {isListening && (
          <>
            <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-40" />
            <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-20 animation-delay-300" />
          </>
        )}
        {isListening ? (
          <StopIcon className="w-8 h-8 text-white relative z-10" />
        ) : (
          <MicrophoneIcon className="w-8 h-8 text-white relative z-10" />
        )}
      </button>

      <p className="text-sm text-slate-400">
        {isListening ? t('listening') : t('tap_to_speak')}
      </p>

      {transcript && (
        <p className="text-sm text-white bg-slate-700/50 rounded-xl px-3 py-2 max-w-xs text-center">
          "{transcript}"
        </p>
      )}
      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}
