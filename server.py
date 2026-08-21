"""Веб-сервер на Python для обработки прототипов страниц Bootstrap.

Реализует полноценную маршрутизацию статических HTML-страниц,
кастомную обработку ошибок 404/500 через шаблоны,
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
            if file_path != "templates/404.html":
                self.handle_error_404()
            else:
                self._send_fallback_error(404, "404 Ошибка: Шаблон не найден")
        except Exception as e:
            print(f"Внутренняя ошибка сервера: {e}")
            self.handle_error_500()

    def do_GET(self) -> None:
        """Маршрутизация входящих GET-запросов.

        Связывает пути навигации с физическими файлами в папке templates.
        """
        clean_path = self.path.split('?')[0]

        if clean_path in ("/", "/index.html"):
            self.send_html_response("templates/index.html")
        elif clean_path == "/categories.html":
            self.send_html_response("templates/categories.html")
        elif clean_path == "/orders.html":
            self.send_html_response("templates/orders.html")
        elif clean_path == "/contacts.html":
            self.send_html_response("templates/contacts.html")
        else:
            self.handle_error_404()

    def do_POST(self) -> None:
        """Обработка входящих POST-запросов и вывод параметров в консоль."""
        if self.path == "/submit-feedback":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length).decode("utf-8")
                parsed_data = urllib.parse.parse_qs(post_data)

                print("\n" + "=" * 40)
                print("[ДАННЫЕ ФОРМЫ ОБРАТНОЙ СВЯЗИ]")
                print(f"Имя: {parsed_data.get('name', [''])}")
                print(f"Почта: {parsed_data.get('email', [''])}")
                print(f"Сообщение: {parsed_data.get('message', [''])}")
                print("=" * 40 + "\n")

                self.send_response(303)
                self.send_header("Location", "/contacts.html")
                self.end_headers()
            except Exception as e:
                print(f"Ошибка при обработке POST: {e}")
                self.handle_error_500()
        else:
            self.handle_error_404()

    def handle_error_404(self) -> None:
        """Дополнительный функционал: Возвращает кастомную страницу ошибки 404."""
        if os.path.exists("templates/404.html"):
            self.send_html_response("templates/404.html", 404)
        else:
            self._send_fallback_error(404, "404 Ошибка: Страница не найдена")

    def handle_error_500(self) -> None:
        """Дополнительный функционал: Возвращает кастомную страницу ошибки 500."""
        if os.path.exists("templates/500.html"):
            self.send_html_response("templates/500.html", 500)
        else:
            self._send_fallback_error(500, "500 Внутренняя ошибка сервера")

    def _send_fallback_error(self, status_code: int, message: str) -> None:
        """Отправляет простой HTML в случае отсутствия физических файлов ошибок."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"<h1>{message}</h1>".encode("utf-8"))


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
