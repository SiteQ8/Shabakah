# Launch the Shabakah guide on interactive SSH login shells.
# It is only called, never exec'd, so leaving the guide drops you at a shell.
case "$-" in
    *i*) ;;
    *) return 2>/dev/null || true ;;
esac

if [ -n "$SSH_CONNECTION" ] && [ -z "$SHABAKAH_STARTED" ] && [ -t 1 ]; then
    SHABAKAH_STARTED=1
    export SHABAKAH_STARTED
    if command -v netsec >/dev/null 2>&1; then
        netsec
    fi
fi
