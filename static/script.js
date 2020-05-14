'use strict';

;
(function(document, window, index) {
    // feature detection for drag&drop upload
    var isAdvancedUpload = function() {
        var div = document.createElement('div');
        return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
    }();


    // applying the effect for every form
    var forms = document.querySelectorAll('.box');
    Array.prototype.forEach.call(forms, function(form) {
        var input = form.querySelector('input[type="file"]'),
            label = form.querySelector('label'),
            errorMsg = form.querySelector('.box__error span'),
            restart = form.querySelectorAll('.box__restart'),
            droppedFiles = false,
            showFiles = function(files) {
                label.textContent = files.length > 1 ? (input.getAttribute('data-multiple-caption') || '').replace('{count}', files.length) : files[0].name;
            },
            triggerFormSubmit = function() {
                var event = document.createEvent('HTMLEvents');
                event.initEvent('submit', true, false);
                form.dispatchEvent(event);
            };

        // letting the server side to know we are going to make an Ajax request
        var ajaxFlag = document.createElement('input');
        ajaxFlag.setAttribute('type', 'hidden');
        ajaxFlag.setAttribute('name', 'ajax');
        ajaxFlag.setAttribute('value', 1);
        form.appendChild(ajaxFlag);

        // automatically submit the form on file select
        input.addEventListener('change', function(e) {
            showFiles(e.target.files);


        });

        // drag&drop files if the feature is available
        if (isAdvancedUpload) {
            form.classList.add('has-advanced-upload'); // letting the CSS part to know drag&drop is supported by the browser

            ['drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop'].forEach(function(event) {
                form.addEventListener(event, function(e) {
                    // preventing the unwanted behaviours
                    e.preventDefault();
                    e.stopPropagation();
                });
            });
            ['dragover', 'dragenter'].forEach(function(event) {
                form.addEventListener(event, function() {
                    form.classList.add('is-dragover');
                });
            });
            ['dragleave', 'dragend', 'drop'].forEach(function(event) {
                form.addEventListener(event, function() {
                    form.classList.remove('is-dragover');
                });
            });
            form.addEventListener('drop', function(e) {
                droppedFiles = e.dataTransfer.files; // the files that were dropped
                showFiles(droppedFiles);

            });
        }


        // if the form was submitted
        form.addEventListener('submit', function(e) {
            // preventing the duplicate submissions if the current one is in progress
            if (form.classList.contains('is-uploading')) return false;

            form.classList.add('is-uploading');
            form.classList.remove('is-error');

            if (isAdvancedUpload) // ajax file upload for modern browsers
            {
                e.preventDefault();

                // gathering the form data
                var ajaxData = new FormData(form);
                if (droppedFiles) {
                    Array.prototype.forEach.call(droppedFiles, function(file) {
                        ajaxData.append(input.getAttribute('name'), file);
                    });
                }

                // ajax request
                var ajax = new XMLHttpRequest();
                ajax.responseType = 'blob';
                ajax.open(form.getAttribute('method'), form.getAttribute('action'), true);

                ajax.onload = function() {
                    form.classList.remove('is-uploading');
                    
                    if (this.status === 200) {
                        var filename = "";
                        var disposition = ajax.getResponseHeader('Content-Disposition');
                        if (disposition && disposition.indexOf('attachment') !== -1) {
                            // Server returned attachment
                            form.classList.add('is-success');
                            var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                            var matches = filenameRegex.exec(disposition);
                            if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                            
                            var type = ajax.getResponseHeader('Content-Type');
                    
                            var blob = typeof File === 'function'
                                ? new File([this.response], filename, { type: type })
                                : new Blob([this.response], { type: type });
                            if (typeof window.navigator.msSaveBlob !== 'undefined') {
                                window.navigator.msSaveBlob(blob, filename);
                            } else {
                                var URL = window.URL || window.webkitURL;
                                var downloadUrl = URL.createObjectURL(blob);
                    
                                if (filename) {
                                    // use HTML5 a[download] attribute to specify filename
                                    var a = document.createElement("a");
                                    // safari doesn't support this yet
                                    if (typeof a.download === 'undefined') {
                                        window.location = downloadUrl;
                                    } else {
                                        a.href = downloadUrl;
                                        a.download = filename;
                                        document.body.appendChild(a);
                                        a.click();
                                    }
                                } else {
                                    window.location = downloadUrl;
                                }
                                setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
                            }
                        } else {
                            // Server returned error message
                            var reader = new FileReader();
                            reader.onload = function() {
                                errorMsg.textContent = reader.result;
                                form.classList.add('is-error');
                            }
                            reader.readAsText(ajax.response);
                        }
                    }
                };

                ajax.onerror = function() {
                    form.classList.remove('is-uploading');
                    alert('Error. Please, try again!');
                };

                ajax.send(ajaxData);
            }
        });

        // restart the form if has a state of error/success
        Array.prototype.forEach.call(restart, function(entry) {
            entry.addEventListener('click', function(e) {
                e.preventDefault();
                form.classList.remove('is-error', 'is-success');
                input.click();
            });
        });

        // Firefox focus bug fix for file input
        input.addEventListener('focus', function() {
            input.classList.add('has-focus');
        });
        input.addEventListener('blur', function() {
            input.classList.remove('has-focus');
        });

    });
}(document, window, 0));