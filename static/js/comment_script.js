    $(document).ready(function() {
        var textInput = $('textarea[name="text"]');
        var previewDiv = $('#comment-preview');
        var validationMessage = $('#validation-message');
        var italicBtn = $('#italic-btn');
        var strongBtn = $('#strong-btn');
        var codeBtn = $('#code-btn');
        var linkBtn = $('#link-btn');

        textInput.on('input', function() {
            var text = textInput.val();

            // Попередній перегляд
            $.ajax({
                type: 'POST',
                url: '{% url "preview_comment" %}',  // Замініть на відповідний URL
                data: {
                    'csrfmiddlewaretoken': '{{ csrf_token }}',
                    'text': text
                },
                success: function(response) {
                    previewDiv.html(response.preview);
                }
            });
        });

        italicBtn.on('click', function(e) {
            e.preventDefault();
            insertTag('<i></i>');
        });

        strongBtn.on('click', function(e) {
            e.preventDefault();
            insertTag('<strong></strong>');
        });

        codeBtn.on('click', function(e) {
            e.preventDefault();
            insertTag('<code></code>');
        });

        linkBtn.on('click', function(e) {
            e.preventDefault();
            insertTag('<a href=""></a>');
        });

        $('#comment-form').on('submit', function(event) {
            event.preventDefault();
            var text = textInput.val();

            // Валідація на стороні клієнта
            if (containsSqlKeywords(text)) {
                validationMessage.text('Введення SQL-команд заборонено.');
                return;
            } else {
                validationMessage.empty();
            }

            // Відправити форму на сервер, якщо дані валідні
            $.ajax({
                type: 'POST',
                url: '{% url "create_comment" %}',  // Замініть на відповідний URL
                data: {
                    'csrfmiddlewaretoken': '{{ csrf_token }}',
                    'text': text
                },
                success: function(response) {
                    if (response.success) {
                        alert(response.message);  // Відобразити повідомлення про успішне створення коментаря
                        window.location.href = '{% url "comment_list" %}';  // Виконати редірект
                    } else {
                        validationMessage.text('Помилка при створенні коментаря.');
                        // Відобразити помилки валідації, якщо є
                    }
                },
                error: function(xhr, textStatus, errorThrown) {
                    validationMessage.text('Помилка при відправці запиту.');
                    console.log(xhr.responseText);  // Вивести додаткову інформацію про помилку
                }
            });
        });

        function insertTag(tag) {
            var currentText = textInput.val();
            var newText = currentText + tag;
            textInput.val(newText);
        }

        function containsSqlKeywords(text) {
            var sqlKeywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE'];
            var regex = new RegExp('\\b(' + sqlKeywords.join('|') + ')\\b', 'i');
            return regex.test(text);
        }
    });