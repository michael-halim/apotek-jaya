$(function () {
  	function initEmployeessDataTable(options = { columnDefs :{}}) {
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

            columnDefs: options.columnDefs,
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
                    initDepartmentsDataTable();
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

					if (!result.is_view_only){
						dselect(document.querySelector('select#employees'), {
							search: true,
						});
						dselect(document.querySelector('select#group'), {
							search: true,
                            clearable:true,
						});
					}
					
					options_datatables = {
						columnDefs: [
							{
								targets: 0,
								visible:false,
								searchable:false,
							},
							{
								targets: 1,
								visible:false,
								searchable:false,
							},
							{
								targets: -1,
								width: '30px',
							},
						],
					};
					initEmployeesFooter();
					employee_datatable = initEmployeessDataTable(options_datatables);
					for(const emp in result.employee_data){
						employee_datatable.row.add([
							result.employee_data[emp]['uq'],
							result.employee_data[emp]['uq_group'],
							result.employee_data[emp]['nik_email'],
							result.employee_data[emp]['name'],
							result.employee_data[emp]['address'],
							result.employee_data[emp]['education'],
							result.employee_data[emp]['permission_group'],
							result.employee_data[emp]['join_date'],
							result.employee_data[emp]['expired_at'],
							result.employee_data[emp]['action'],
						]).draw(true);
					}

					$('#departments-employees-table').css({'width':'100%',});
					$('th#uq').css({'display':'none',})
					$('th#uq-group').css({'display':'none',})

					if (result.is_view_only) {
						$('#departments-employees-table > tbody > tr').css({
							'background-color': '#e9ecef',
						});
					}
					$('#form-departments-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-departments', function () {
		let form = document.getElementById('add_departments_form');
		let form_data = new FormData(form);
		
		employees = employee_datatable.rows().data().toArray();
        console.log(employees);
		let employees_data = [];
        let employees_permission_group_data = [];
		for (const emp of employees) {
			employees_data.push(emp[0]);
            employees_permission_group_data.push(emp[1])
		}

		form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
		form_data.delete('employees');
		form_data.delete('departments-employees-table_length');
		form_data.append('employees[]',employees_data);
		form_data.append('employees_permission_group[]',employees_permission_group_data);

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

                    initDepartmentsDataTable();

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
                
                $('#form-departments-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

	$('body').on('click', '#add-employee-departments', function () {
		$.ajax({
            url: 'add-employees/',
            method: 'POST',
            data: {
                employees: $('select#employees').val(),
                permission_group : $('select#group').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (result) {
                if (result.success === true) {
                    let dept_emp_data = [
                        result.employee_data['uq'],
                        result.employee_data['uq_group'],
                        result.employee_data['nik_email'],
                        result.employee_data['name'],
                        result.employee_data['address'],
                        result.employee_data['education'],
                        result.employee_data['permission_group'],
                        result.employee_data['join_date'],
                        result.employee_data['expired_at'],
                        result.employee_data['action'],
                    ];

                    let current_data = employee_datatable.rows().data();

                    let is_exist = false;
                    for (const key of current_data.toArray()){
                        if (key[0] === dept_emp_data[0]){
                            is_exist = true;
                            break;
                        }
                    }

                    if (!is_exist){
                        options_datatables = {
                            columnDefs: [
                            {
                                targets: 0,
                                visible:false,
                                searchable:false,
                            },
                            {
                                targets: 1,
                                visible:false,
                                searchable:false,
                            },
                            {
                                targets: -1,
                                width: '30px',
                            },
                            ],
                        };
                        employee_datatable = initEmployeessDataTable(options_datatables);
                        employee_datatable.row.add(dept_emp_data).draw(true);
                    }
                    else{
                        toastr['error']('Employee Already Exist in This Departments');
                    }
                
                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error: function (result) {},
		});
	});

	$('body').on('click', '.delete-departments-employees', function () {
		employee_datatable.row($(this).parents('tr')).remove().draw();

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
