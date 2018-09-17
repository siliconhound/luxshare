from werkzeug.http import parse_cookie

def get_cookie(response, name, type=str, flags=None, except_flags=None):
    cookies = response.headers.getlist('Set-Cookie')
    for cookie in cookies:
        c = parse_cookie(cookie)
        if name in c:
            if flags is not None and except_flags is None:
                all_flags = True
                for flag in flags:
                    if flag not in cookie:
                        all_flags = False
                        break
                
                if all_flags:
                    return c.get(name, type=type)
                else:
                    continue

            if except_flags is not None:
                all_flags = True
                for flag in except_flags:
                    if flag in cookie:
                        all_flags = False
                        break
                
                if all_flags:
                    return c.get(name, type=type)
                else:
                    continue
            return c.get(name, type=type)
    
    return ""

def get_raw_cookie(response, name, type=str):
    cookies = response.headers.getlist('Set-Cookie')
    for cookie in cookies:
        c = parse_cookie(cookie)
        if name in c:
            return cookie
    
    return ""