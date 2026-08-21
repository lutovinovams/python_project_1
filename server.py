"""Веб-сервер на чистом Python для обработки прототипов страниц Bootstrap.

Реализует отдачу статических HTML-страниц, обработку ошибок 404/500,
а также прием и парсинг POST-запросов из формы обратной связи.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

PORT = 8000


class MyBootstrapServer(BaseHTTPRequestHandler):
    """Кастомный обработчик HTTP-запросов для Bootstrap-приложения."""

    def send_html_response(self, file_path: str, status_code: int = 200) -> None:
        """Считывает HTML-файл через контекстный менеджер и отправляет его клиенту.

        Args:
            file_path: Путь к файлу шаблона.
            status_code: HTTP статус-код ответа.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            self.send_response(status_code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except FileNotFoundError:
            self.handle_error_404()
        except Exception as e:
            print(f"Внутренняя ошибка сервера: {e}")
            self.handle_error_500()

    def do_GET(self) -> None:
        """Маршрутизация входящих GET-запросов."""
        if self.path == "/" or self.path == "/index.html":
            self.send_html_response("templates/index.html")
        elif self.path == "/contacts.html":
            self.send_html_response("templates/contacts.html")
        else:
            self.handle_error_404()

    def do_POST(self) -> None:
        """Обработка входящих POST-запросов и вывод параметров в консоль."""
        if self.path == "/submit-feedback":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            parsed_data = urllib.parse.parse_qs(post_data)

            print("\n" + "=" * 40)
            print("[ДАННЫЕ ФОРМЫ ОБРАТНОЙ СВЯЗИ]")
            print(f"Имя: {parsed_data.get('name', [''])[0]}")
            print(f"Почта: {parsed_data.get('email', [''])[0]}")
            print(f"Сообщение: {parsed_data.get('message', [''])[0]}")
            print("=" * 40 + "\n")

            self.send_response(303)
            self.send_header("Location", "/contacts.html")
            self.end_headers()
        else:
            self.handle_error_404()

    def handle_error_404(self) -> None:
        """Возвращает кастомную страницу ошибки 404."""
        if os.path.exists("templates/404.html"):
            self.send_html_response("templates/404.html", 404)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>404 Ошибка: Страница не найдена</h1>".encode("utf-8"))

    def handle_error_500(self) -> None:
        """Возвращает кастомную страницу ошибки 500."""
        if os.path.exists("templates/500.html"):
            self.send_html_response("templates/500.html", 500)
        else:
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>500 Внутренняя ошибка сервера</h1>".encode("utf-8"))


def run() -> None:
    """Инициализирует и запускает HTTP-сервер."""
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, MyBootstrapServer)
    print(f"Сервер запущен на http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        httpd.server_close()


if __name__ == "__main__":
    run()
