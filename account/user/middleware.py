import time

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import http_date

from django.contrib.sessions.middleware import SessionMiddleware
from datetime import datetime, timezone, timedelta
import time, jwt


class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        tmp_session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        session_key = tmp_session_key
        is_provisional_login = False
        is_provisional_signup = False
        jwt_decode = ""
        exp = ""
        user_id = "-1"
        try:
            if tmp_session_key is not None:
                jwt_decode = jwt.decode(
                    tmp_session_key,
                    getattr(settings, "JWT_SECRET_KEY", None),
                    leeway=5,  # 通信上の遅延で５秒遅くても大丈夫ないように
                    algorithms=["HS256"],
                )
                session_key = jwt_decode["session_key"]
                if "is_login" in jwt_decode:
                    is_provisional_login = jwt_decode["is_login"]
                if "is_signup" in jwt_decode:
                    is_provisional_signup = jwt_decode["is_signup"]
                if "exp" in jwt_decode:
                    exp = jwt_decode["exp"]
                if "sub" in jwt_decode:
                    user_id = jwt_decode["sub"]
        except jwt.ExpiredSignatureError:
            # 有効期限が過ぎたらここに入る
            pass
        except jwt.exceptions.DecodeError:
            # デコードに失敗したら(編集されていても)ここに入る
            pass
        request.session = self.SessionStore(session_key)
        request.session["is_provisional_login"] = is_provisional_login
        request.session["is_provisional_signup"] = is_provisional_signup
        request.session["exp"] = exp
        request.session["user_id"] = user_id

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie or delete
        the session cookie if the session has been emptied.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response
        # First check if we need to delete this cookie.
        # The session should be deleted only if the session is entirely empty.
        if settings.SESSION_COOKIE_NAME in request.COOKIES and empty:
            response.delete_cookie(
                settings.SESSION_COOKIE_NAME,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 5xx responses.
                if response.status_code < 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )

                    id = ""
                    email = ""
                    is_provisional_login = False
                    is_provisional_signup = False
                    exp = datetime.now(tz=timezone.utc) + timedelta(seconds=14400)
                    if "is_provisional_login" in request.session:
                        is_provisional_login = request.session["is_provisional_login"]
                    if "is_provisional_signup" in request.session:
                        is_provisional_signup = request.session["is_provisional_signup"]
                    if (is_provisional_login is True) or (
                        is_provisional_signup is True
                    ):
                        if "exp" in request.session:
                            exp = datetime.fromtimestamp(float(request.session["exp"]))
                            id = request.session["user_id"]
                    jwt_session_key = jwt.encode(
                        {
                            "session_key": request.session.session_key,
                            "iss": "http://localhost",
                            "sub": id,
                            "email": email,
                            "is_login": is_provisional_login,
                            "is_signup": is_provisional_signup,
                            "exp": exp,
                            "iat": datetime.now(tz=timezone.utc),
                        },
                        getattr(settings, "JWT_SECRET_KEY", None),
                        algorithm="HS256",
                    )
                    response.set_cookie(
                        settings.SESSION_COOKIE_NAME,
                        jwt_session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
        return response