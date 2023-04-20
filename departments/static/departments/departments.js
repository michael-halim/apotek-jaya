$(function () {
  function initEmployeessDataTable(){
    $('#departments-employees-table').DataTable().destroy();
    let employee_datatable = $('#departments-employees-table').DataTable({
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
        index:true,
        responsive: true,
    });
    return employee_datatable;
  }

function initEmployeesFooter(){
    $('#departments-employees-table tfoot th.search-text').each(function () {
        var title = $(this).text();
        $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
    });
}
  function initDepartmentsDataTable() {
    $('#departments-table').DataTable().destroy();
    $('#departments-table').DataTable({
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
        url: 'fetch-departments/',
        dataSrc: 'departments_data',
      },
      responsive: true,
      columnDefs: [{ targets: 3, width: '90px' }],
      columns: [
        {
          data: 'name',
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
          },
        },
        {
          data: 'uq',
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
  let employee_datatable = null;
  initDepartmentsDataTable();
  $('body').on('click', '.delete-departments', function () {
    if (confirm('Do You Want to Deactivate this Department ?')) {
      let department_uuid = $(this).data('uq');
      let url = $(this).data('link');
      url = url.replace('@@', department_uuid);

      $.ajax({
        url: url,
        method: 'POST',
        data: {
          csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function (result) {
          if (result.success === true) {
            initDataTable();
          } else if (result.success === false) {
            toastr['error'](result.toast_message);
          }
        },
        error: function (result) {},
      });
    }
  });
  $('body').on('click','.update-departments, .view-departments, #add-departments', function () {
      let department_uuid = $(this).data('uq');
      let url = $(this).data('link');
      url = url.replace('@@', department_uuid);

      $.ajax({
        url: url,
        method: 'GET',
        success: function (result) {
          if (result.success === true) {
            $('#form-departments-modal .modal-content').html(result.form);
            dselect(document.querySelector('select#user'), {
              search: true,
            });

            employee_datatable = initEmployeessDataTable();

            $('#emp').css({
              'width':'100%',
            });

            initEmployeesFooter();
            
            $('#form-departments-modal').modal('show');
            
          } else if (result.success === false) {
            toastr['error'](result.toast_message);
          }
        },
        error: function (result) {},
      });
    }
  );
  $('body').on('click', '#submit-form-departments', function () {
    let form = document.getElementById('add_departments_form');
    let form_data = new FormData(form);
    form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

    let department_uuid = $(this).data('uq');
    let url = $(this).data('link');
    url = url.replace('@@', department_uuid);

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

          $('.modal-messages').css({ display: 'block' }).html(messages_element);

          toastr['error'](result.toast_message);
        }

        $('#form-departments-modal').modal(
          result.is_close_modal === true ? 'hide' : 'show'
        );
      },
      error: function (result) {},
    });
  });
  $('body').on('click', '#add-employee-departments', function () {
    $.ajax({
      url: 'add-employees/',
      method: 'POST',
      data: {
        user: $('select#user').val(),
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
      },
      success: function (result) {
        if (result.success === true) {
            const dept_emp_data = [];
            for (const key in result.employee_data) {
                dept_emp_data.push(result.employee_data[key]);
            }
            let current_data = employee_datatable.rows().data();

            let is_exist = false;
            for (const key of current_data.toArray()){
                if (key[0] === dept_emp_data[0]){
                    is_exist = true;
                    break;
                }
            }

            if (!is_exist){
              employee_datatable.row.add(dept_emp_data).draw(true);
              employee_datatable = initEmployeessDataTable();
            }
            else{
              toastr['error']('Employee Already Exist in This Departments');
            }
          
        } else if (result.success === false) {
        }
      },
      error: function (result) {},
    });
  });
  $('#departments-table tfoot th.search-text').each(function () {
    var title = $(this).text();
    $(this).html(
      '<input class="form-control" type="text" placeholder="Search ' +
        title +
        '" />'
    );
  });
  
});
