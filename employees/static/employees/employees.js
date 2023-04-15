$(function () {
    function initDataTable(){
        $('#emp').DataTable().destroy();
        $('#emp').DataTable({
            initComplete: function () {
                // Apply the search
                this.api()
                    .columns()
                    .every(function () {
                        var that = this;

                        $('input', this.footer()).on('keyup change clear', function () {
                            if (that.search() !== this.value) {
                                that.search(this.value).draw();
                            }
                        });
                    });
            },

            ajax: {
                url: 'fetch-employees/',
                dataSrc: 'employees_data',
            },
            responsive: true,
            columnDefs: [
                { targets: 4, width: "80px" },
                { targets: 5, width: "100px" },
            ],
            columns: [
                {
                    data: 'nik',
                    defaultContent: '-',
                },
                {
                    data: 'name',
                    defaultContent: '-',
                },
                {
                    data: 'address',
                    defaultContent: '-',
                },
                {
                    data: 'created_at',
                    defaultContent: '-',
                },
                {
                    data: 'status',
                    render: function (data, type, row) {
                        if (data === 1) {
                            return '<span class="badge bg-success">Active</span>';
                        } else if (data === 0) {
                            return '<span class="badge bg-danger">Inactive</span>';
                        } else {
                            return '<span class="badge bg-secondary">Unknown</span>';
                        }
                    }
                },
                {
                    data: 'uq',
                    render: function (data, type, row) {
                        let element = `
                            <div class="d-flex justify-content-center">
                                <span data-uq=${data.hash} class="view-employees btn text-primary me-3">
                                    <i class="bi bi-eye"></i>
                                </span>
                                <span data-uq=${data.hash} data-link=${data.update_link} class="update-employees btn text-warning me-3">
                                    <i class="bi bi-pencil"></i>
                                </span>
                                <span data-uq=${data.hash} class="delete-employees btn text-danger">
                                    <i class="bi bi-trash"></i>
                                </span>
                            </div>`;
                        return element;

                    }
                },
            ],
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],

        });
    }
    
    initDataTable();

    toastr.options = {
        closeButton: false,
        debug: false,
        newestOnTop: false,
        progressBar: true,
        positionClass: 'toast-top-right',
        preventDuplicates: false,
        onclick: null,
        showDuration: '300',
        hideDuration: '1000',
        timeOut: '5000',
        extendedTimeOut: '1000',
        showEasing: 'swing',
        hideEasing: 'linear',
        showMethod: 'fadeIn',
        hideMethod: 'fadeOut',
    };

    
    $('body').on('click', '.update-employees', function () {
        let employee_uuid = $(this).data('uq');
        let url = $(this).data('link');
        url = url.replace('@@', employee_uuid);
            
        $.ajax({
            url: url,
            method: 'GET',
            success: function (result) {
                $('#add-employees-modal .modal-content').html(result.form);
                $('#add-employees-modal').modal('show');
            },
            error: function (result) {

            },
        });
    });
    $('body').on('click', '#submit-update-employees', function () {
        let form = document.getElementById('add_employees_form');
        let form_data = new FormData(form);
        form_data.append(
            'csrfmiddlewaretoken',
            $('input[name=csrfmiddlewaretoken]').val()
        );
        let employee_uuid = $(this).data('uq');
        let url = $(this).data('link');
        url = url.replace('@@', employee_uuid);
        
        $.ajax({
            url: url,
            method: 'POST',
            processData: false,
            contentType: false,
            data: form_data,
            success: function (result) {
                $('.form-error').html('');
                $('.is-invalid').removeClass('is-invalid');

                if (result.success === true){
                    $('.modal-messages').css({ display: 'none' }).html('');
                    toastr['success'](result.toast_message);

                    initDataTable();
                    
                }
                else if (result.success === false) {
                    for (const keys in result.errors) {
                        $('#' + keys).addClass('is-invalid');

                        let error_list = '';
                        for (const err of result.errors[keys]) {
                            error_list += err + '<br>';
                        }

                        $('#' + keys).next('.form-error').html(error_list);
                    }

                    let messages_element = '';
                    for (const message of result.modal_messages) {
                        messages_element += `<li class= "${message.tags}">${message.message}</li>`;
                    }

                    $('.modal-messages').css({ display: 'block' }).html(messages_element);

                    toastr['error'](result.toast_message);
                }
                
                $('#add-employees-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) { 

            },
        });
    });
    $('body').on('click', '#add-employees', function () {
        const url = $(this).data('link');
        $.ajax({
            url: url,
            method: 'GET',
            success: function (result) {
                $('#add-employees-modal .modal-content').html(result.form);
                $('#add-employees-modal').modal('show');
            },
            error: function (result) {

            },
        });
    });
    $('body').on('click', '#submit-add-employees', function () {
        let form = document.getElementById('add_employees_form');
        let form_data = new FormData(form);
        form_data.append(
            'csrfmiddlewaretoken',
            $('input[name=csrfmiddlewaretoken]').val()
        );
        const url = $(this).data('link');

        $.ajax({
            url: url,
            method: 'POST',
            processData: false,
            contentType: false,
            data: form_data,
            success: function (result) {
                $('.form-error').html('');
                $('.is-invalid').removeClass('is-invalid');

                if (result.success === true){
                    $('.modal-messages').css({ display: 'none' }).html('');
                    toastr['success'](result.toast_message);

                    initDataTable();
                    
                }
                else if (result.success === false) {
                    for (const keys in result.errors) {
                        $('#' + keys).addClass('is-invalid');

                        let error_list = '';
                        for (const err of result.errors[keys]) {
                            error_list += err + '<br>';
                        }

                        $('#' + keys).next('.form-error').html(error_list);
                    }

                    let messages_element = '';
                    for (const message of result.modal_messages) {
                        messages_element += `<li class= "${message.tags}">${message.message}</li>`;
                    }

                    $('.modal-messages').css({ display: 'block' }).html(messages_element);

                    toastr['error'](result.toast_message);
                }
                
                $('#add-employees-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) { 

            },
        });
    });

    $('#emp tfoot th.search-text').each(function () {
        var title = $(this).text();
        $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
    });

});