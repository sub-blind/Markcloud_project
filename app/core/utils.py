def get_chosung(text: str) -> str:
    """
    한글 텍스트에서 초성을 추출하는 함수

    Args:
        text: 한글 텍스트

    Returns:
        str: 초성

    Examples:
        >>> get_chosung("안녕하세요")
        'ㅇㅇㅎㅅ'
    """
    if not text:
        return ""
    
    CHOSUNG = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    result = []

    for char in text:
        if '가' <= char <= '힣':
            # 한글 유니코드 분해
            chosung_index = (ord(char) - ord('가')) // 588
            result.append(CHOSUNG[chosung_index])
        else:
            result.append(char)

    return ''.join(result)

def is_chosung(text: str) -> bool:
    """
    초성으로만 이루어져 있는지

    Args:
        text: 텍스트
    
    Returns:
        true
    """
    if not text:
        return False
    
    CHOSUNG = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    return all(char in CHOSUNG for char in text)