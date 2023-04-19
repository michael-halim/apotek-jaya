$(function () {
    function initDataTable(){
        $('#permission-table').DataTable().destroy();
        $('#permission-table').DataTable({
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
                url: 'list-permission/',
                dataSrc: 'permission_data',
            },
            responsive: true,
            columnDefs: [
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
                    data: 'department',
                    defaultContent: '-',
                },
                {
                    data: 'group_name',
                    defaultContent: '-',
                },
                {
                    data: 'permission',
                    defaultContent: '-',
                },
                {
                    data: 'uq',
                    defaultContent: '-',
                },
            ],
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],

        });
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

    initDataTable();
    
    $('body').on('click','.update-permission, .view-permission, #add-permission',function () {
        let url = $(this).data('link');

        $.ajax({
          url: url,
          method: 'GET',
          success: function (result) {
            if (result.success === true) {
              $('#form-permission-modal .modal-content').html(result.form);
              $('#form-permission-modal').modal('show');
            } else if (result.success === false) {
              toastr['error'](result.toast_message);
            }
          },
          error: function (result) {},
        });
      }
    );
    
    $('body').on('click', '#submit-form-permission', function () {
      let form = document.getElementById('add_permission_form');
      let form_data = new FormData(form);
      console.log(form_data);
      form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

      let url = $(this).data('link');
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

            initDataTable();
            
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

          $('#form-permission-modal').modal(
            result.is_close_modal === true ? 'hide' : 'show'
          );
        },
        error: function (result) {},
      });
    });

    $('body').on('click', '#check-all-permissions', function () {
      $('input:checkbox[name="permissions"], input:checkbox[id *="check-all-group"]')
        .not(this)
        .prop('checked', this.checked);
    });

    $('body').on('click', 'input[type="checkbox"][id *="check-all-group"]',function () {
        
        let id = $(this).attr('id').replace('check-all-group-','').trim();
        let start = parseInt(id);
        for (let i = start; i <= start + 3; i++) {
            let selector = '#id_permissions_' + i.toString();
            $(selector).not(this).prop('checked', this.checked);
        } 
    });

    $('#permission-table tfoot th.search-text').each(function () {
        var title = $(this).text();
        $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
    });

});