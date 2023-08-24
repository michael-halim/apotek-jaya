$(function () {
    function format_date(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${year}-${month}-${day}T${hours}:${minutes}`;

    }

    function initOvertimeUsersDataTable(options = { columnDefs :{}}) {
		$('#overtimes-users-table').DataTable().destroy();
		let overtime_users_datatable = $('#overtimes-users-table').DataTable({
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

            paging: false,
            responsive: true,
            columnDefs: options.columnDefs,
		});

        return overtime_users_datatable;
	}

    function initOvertimeUsersFooter() {
        $('#overtimes-users-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
        });
    }

	function initOvertimesDataTable() {
		$('#overtimes-table').DataTable().destroy();
		let overtimes_datatable = $('#overtimes-table').DataTable({
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
                url: 'fetch-overtimes/',
                dataSrc: 'overtimes_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width: '90px' }],
            columns: [
                {
                    data: 'name',
                    defaultContent: '-',
                },
                {
                    data: 'description',
                    defaultContent: '-',
                },
                {
                    data: 'start_at',
                    defaultContent: '-',
                },
                {
                    data: 'end_at',
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
		});

        return overtimes_datatable;
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

	let overtimes_datatable =  initOvertimesDataTable();
    let overtime_users_datatable = null;

	$('body').on('click', '.delete-overtimes', function () {
		if (confirm('Do You Want to Deactivate this Overtime ?')) {
            let overtime_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', overtime_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        overtimes_datatable = initOvertimesDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-overtimes, .view-overtimes, #add-overtimes', function () {
		let overtime_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', overtime_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
                    console.log(result);
					$('#form-overtimes-modal .modal-content').html(result.form);
                    
                    if (!result.is_view_only){
                        dselect(document.querySelector('select#employee_id'), {
                            search: true,
                            clearable: true,
                        });
                    }
                    
                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                        ],
                    };

                    initOvertimeUsersFooter();
                    overtime_users_datatable = initOvertimeUsersDataTable(options_datatables);
                    for(const key in result.overtime_users_data){
                        let status = '<span class="badge bg-secondary">Unknown</span>';
                        if (result.overtime_users_data[key]['status'] === 1) status = '<span class="badge bg-success">Active</span>';
                        else if (result.overtime_users_data[key]['status'] === 0) status = '<span class="badge bg-danger">Inactive</span>';

                        overtime_users_datatable.row
                          .add([
                            result.overtime_users_data[key]['uq_employee'],
                            result.overtime_users_data[key]['nik_name'],
                            result.overtime_users_data[key]['departments'],
                            status,
                            result.overtime_users_data[key]['action'],
                          ])
                          .draw(true);
                    }

                    $('th#uq-employee').css({ display: 'none' });
                    $('#overtimes-users-table').css({ width: '100%' });

					$('#form-overtimes-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-overtimes', function () {
		let form = document.getElementById('overtimes_form');
		let form_data = new FormData(form);
        let overtime_users = [];
        
        for (const data of overtime_users_datatable.rows().data().toArray()){
            overtime_users.push(data[0]);
        }
        
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.append('overtime_users[]', overtime_users);

		let overtime_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', overtime_uuid);

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

                    overtimes_datatable = initOvertimesDataTable();

                } else if (result.success === false) {
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
                
                $('#form-overtimes-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('click','#add-overtime-users',function(){
        $.ajax({
            url : 'add-overtimes-users/', 
            method : 'POST', 
            data : {
                employee: $('select#employee_id').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            }, 
            success:function(result){
                if (result.success === true) {

                    let status = '<span class="badge bg-secondary">Unknown</span>';
                    if (result.employee_data['status'] === 1)  status = '<span class="badge bg-success">Active</span>';
                    else if (result.employee_data['status'] === 0) status = '<span class="badge bg-danger">Inactive</span>';
                    
                    let employee_data = [
                        result.employee_data['uq_employee'],
                        result.employee_data['nik_name'],
                        result.employee_data['departments'],
                        status,
                        result.employee_data['action'],
                    ];

                    let current_data = overtime_users_datatable.rows().data();

                    let is_exist = false;
                    for (const key of current_data.toArray()) {
                        if (key[0] === employee_data[0]) {
                            is_exist = true;
                            break;
                        }
                    }

                    if (!is_exist) {
                        options_datatables = {
                            columnDefs: [
                                { targets: 0, visible: false, searchable: false, },
                                { targets: -1, width: '30px', },
                            ],
                        };

                        overtime_users_datatable = initOvertimeUsersDataTable(options_datatables);
                        overtime_users_datatable.row.add(employee_data).draw(true);
                        
                    } else {
                        toastr['error']('Employee Already Exist in This Overtime');
                    }

                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error:function(result){
                
            }
        });
    });

    $('body').on('click', '.delete-overtime-users', function () {
        overtime_users_datatable.row($(this).parents('tr')).remove().draw();
    });

    $('body').on('change','input#start_at, input#end_at',function(){
        let start_at = $('input#start_at').val();
        let end_at = $('input#end_at').val();
        if (start_at !== '' && end_at === '') {
            $('input#end_at').val(start_at);
        } else if (start_at === '' && end_at !== '') {
            $('input#start_at').val(end_at);

        } else if (start_at !== '' && end_at !== '') {
            let start_at_date = new Date(start_at);
            let end_at_date = new Date(end_at);
            if (start_at_date > end_at_date) $('input#end_at').val(start_at);
            else $('input#start_at').val(end_at);
          
        } 
        
    });

	$('#overtimes-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
