import re, webvtt

################################################################################
# Cleaning up VTT format transcription to Nvivo format
_voice_tag_re = re.compile(r'^\s*<v\s+([^>]+)>\s*(.*)$', re.IGNORECASE)  # <v Speaker> text
_colon_tag_re = re.compile(r'^\s*([^\n:]{1,50})\s*[:：]\s*(.+)$')  # Speaker: text
_bracket_tag_re = re.compile(r'^\s*[\[(]([^)\]]{1,50})[\])]\s*[:\-–]?\s*(.+)$')  # [Speaker] text or (Speaker) text


def _extract_speaker_and_text(raw_text, speaker_default):
    """
    Returns (speaker, text) from a caption.
    Tries WebVTT <v Speaker>, 'Speaker: text', and '[Speaker] text' patterns.
    Falls back to (speaker_default, raw_text) if none match.
    """
    # Collapse multiline caption into one line
    text = " ".join(line.strip() for line in raw_text.splitlines()).strip()

    m = _voice_tag_re.match(text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    m = _colon_tag_re.match(text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    m = _bracket_tag_re.match(text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    return speaker_default, text


def _format_hhmmss(timestamp_str):
    """
    Normalizes 'HH:MM:SS.mmm' -> 'HH:MM:SS' (NVivo accepts tenths too;
    keep simple whole seconds by default).
    """
    return timestamp_str.split('.')[0]  # drop milliseconds


def vtt_to_nvivo_txt(vtt_path, out_path, speaker_default="Speaker", keep_fractional=False):
    """
    Convert a VTT to an NVivo-friendly TXT that preserves speaker labels when present.
    Output format:
        HH:MM:SS
        Speaker: content
    (blank line between rows is optional; NVivo is fine without it.)
    """
    rm(out_path)

    rows = []
    for caption in webvtt.read(vtt_path):
        start = caption.start if keep_fractional else _format_hhmmss(caption.start)
        speaker, content = _extract_speaker_and_text(caption.text, speaker_default)

        # Guard against empty content
        if not content:
            continue

        # Compose a 2-line NVivo row: timestamp on one line, "Speaker: text" on next
        rows.append(f"{start}\n{speaker}: {content}")

    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write("\n".join(rows))
