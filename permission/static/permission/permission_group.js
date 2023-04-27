$(function () {
    function initPermissionGroupDataTable(){
        $('#permission-group-table').DataTable().destroy();
        let permission_datatable = $('#permission-group-table').DataTable({
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
                url: 'list-permission-group/',
                dataSrc: 'permission_group_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width:'90px' }],
            columns: [
                {
                    data: 'name',
                    defaultContent: '-',
                },
                {
                    data: 'action',
                    defaultContent: '-',
                },
            ],
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
        });

        return permission_datatable;
    }
    
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

    permission_group_datatable = initPermissionGroupDataTable();
    
    // $('body').on('click', '.delete-permission', function () {
    //     if (confirm('Do You Want to Delete this Permission ?')) {
    //         let employee_uuid = $(this).data('uq');
    //         let url = $(this).data('link');
    //         url = url.replace('@@', employee_uuid);

    //         $.ajax({
    //         url: url,
    //         method: 'POST',
    //         data: {
    //             csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    //         },
    //         success: function (result) {
    //             if (result.success === true) {
    //                 initPermissionDataTable();

    //             } else if (result.success === false) {
    //                 toastr['error'](result.toast_message);

    //             }
    //         },
    //         error: function (result) {},
    //         });
    //     }
    // });

    $('body').on('click','.update-permission-group, .view-permission-group, #add-permission-group',function () {
        let url = $(this).data('link');
        let group_id = $(this).data('uq');
        url = url.replace('@@', group_id);

        $.ajax({
          url: url,
          method: 'GET',
          success: function (result) {
            if (result.success === true) {
                $('#form-permission-group-modal .modal-content').html(result.form);
                
                check_checkbox_grouping();
                
                $('#form-permission-group-modal').modal('show');

            } else if (result.success === false) {
                toastr['error'](result.toast_message);
            }
          },
          error: function (result) {},
        });
      }
    );
    
    $('body').on('click', '#submit-form-permission-group', function () {
        let form = document.getElementById('permission_group_form');
        let form_data = new FormData(form);
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

        let url = $(this).data('link');
        let group_id = $(this).data('uq');
        url = url.replace('@@', group_id);
        $.ajax({
            url: url,
            method: 'POST',
            processData: false,
            contentType: false,
            data: form_data,
            success: function (result) {
                $('.form-error').html('');
                $('.is-invalid').removeClass('is-invalid');

                if (result.success === true) {
                    $('.modal-messages').css({ display: 'none' }).html('');
                    toastr['success'](result.toast_message);

                    permission_datatable = initPermissionGroupDataTable();
                    
                } else if (result.success === false) {
                    
                    for (const keys in result.errors) {
                        $('#' + keys).addClass('is-invalid');

                        let error_list = '';
                        for (const err of result.errors[keys]) {
                            error_list += err + '<br>';
                        }
                        
                        $('#' + keys)
                            .next('.form-error')
                            .html(error_list);
                    }

                    let messages_element = '';
                    for (const message of result.modal_messages) {
                        messages_element += `<li class= "${message.tags}">${message.message}</li>`;
                    }

                    $('.modal-messages')
                    .css({ display: 'block' })
                    .html(messages_element);

                    toastr['error'](result.toast_message);
                }

                $('#form-permission-group-modal').modal(
                    result.is_close_modal === true ? 'hide' : 'show'
                );
            },
            error: function (result) {},
        });
    });

    function check_checkbox_grouping(){
        let count_groups = $('input[id*=check-all-group]').length;
        for (let i = 0; i < count_groups; i++) {
            let name = $('input.form-check-input[name]').attr('name');
            if ( $(`#id_${name}_${i * 4}`).is(':checked') && $(`#id_${name}_${i*4 + 1}`).is(':checked') && 
                $(`#id_${name}_${i*4 + 2}`).is(':checked') && $(`#id_${name}_${i*4 + 3}`).is(':checked') ) {
                    $(`#check-all-group-${i*4}`).prop('checked',true);
            }
        }
    }

    $('body').on('click', '#check-all-permissions', function () {
        $('input:checkbox[name="permissions"], input:checkbox[id *= "check-all-group"]')
            .not(this)
            .prop('checked', this.checked);
    });

    $('body').on('click','input:checkbox[name="permissions"]',function(){
        let id = $(this).attr('id').replace('id_permissions_', '').trim();
        let start = Math.floor(parseInt(id) / 4);
        let is_check_group = true; 
        let is_check_all = true;
        let count_groups = $('input[id*=check-all-group]').length;
        for (let i = 0; i < count_groups; i++) {
            if ( !$(`#id_permissions_${i*4}`).is(':checked') || !$(`#id_permissions_${i*4 + 1}`).is(':checked') || 
                !$(`#id_permissions_${i*4 + 2}`).is(':checked') || !$(`#id_permissions_${i*4 + 3}`).is(':checked')) {
                    is_check_all = false;
                    
                    if (start == i){
                        is_check_group = false;
                        break;
                    }
            }
        }

        $(`#check-all-group-${start*4}`).prop('checked', is_check_group);
        $('#check-all-permissions').prop('checked', is_check_all);
    });

    $('body').on('click', 'input[type="checkbox"][id *="check-all-group"]',function () {
        let id = $(this).attr('id').replace('check-all-group-','').trim();
        let start = parseInt(id);
        for (let i = start; i < start + 4; i++) 
            $(`#id_permissions_${i}`).not(this).prop('checked', this.checked);
        
    });

    $('#permission-group-table tfoot th.search-text').each(function () {
        var title = $(this).text();
        $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
    });

});