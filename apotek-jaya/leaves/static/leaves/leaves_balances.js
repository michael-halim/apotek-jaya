$(function () {
    function initLeavesBalancesEmployeeDataTable(options = { columnDefs :{}}) {
		$('#leaves-balances-employee-table').DataTable().destroy();
		let leaves_balances_employee_datatable = $('#leaves-balances-employee-table').DataTable({
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

        return leaves_balances_employee_datatable;
	}

    function initLeavesBalancesEmployeeFooter() {
        $('#leaves-balances-employee-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
        });
    }

	function initLeavesBalancesDataTable() {
		$('#leaves-balances-table').DataTable().destroy();
		let leaves_balances_datatable = $('#leaves-balances-table').DataTable({
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
                url: 'fetch-leaves-balances/',
                dataSrc: 'leaves_balances_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width: '90px' }],
            columns: [
                {
                    data: 'nik_name',
                    defaultContent: '-',
                },
                {
                    data: 'departments',
                    defaultContent: '-',
                },
                {
                    data: 'expired_at',
                    defaultContent: '-',
                },
                {
                    data: 'uq',
                },
            ],
		});

        return leaves_balances_datatable;
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

    let leaves_balances_datatable = initLeavesBalancesDataTable();
    let leaves_balances_employee_datatable = null;

	$('body').on('click', '.delete-leaves-balances', function () {
		if (confirm('Do You Want to Deactivate this Leave Balance ?')) {
            let leave_balance_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', leave_balance_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        leaves_balances_datatable = initLeavesBalancesDataTable();

                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-leaves-balances, .view-leaves-balances, #add-leaves-balances', function () {
		let leave_balance_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', leave_balance_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
                    console.log(result);
					$('#form-leaves-balances-modal .modal-content').html(result.form);
                    
                    if (result.mode === 'create'){
                        dselect(document.querySelector('select#employee_id'), {
                            search: true,
                            clearable:true,
                        });

                        dselect(document.querySelector('select#leave_id'), {
                            search: true,
                            clearable:true,
                        });
                    } else if (result.mode === 'update') {
                        $('#employee_id').addClass('form-control');
                        dselect(document.querySelector('select#leave_id'), {
                            search: true,
                            clearable:true,
                        });
                    } else{
                        $('#employee_id').addClass('form-control');
                    }


                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                            { targets: -1, width: '30px', },
                        ],
                    };
                    initLeavesBalancesEmployeeFooter();
                    leaves_balances_employee_datatable = initLeavesBalancesEmployeeDataTable(options_datatables);
                    for(const key in result.leaves_balances_data){
                        leaves_balances_employee_datatable.row
                          .add([
                            result.leaves_balances_data[key]['uq_leave'],
                            result.leaves_balances_data[key]['name'],
                            result.leaves_balances_data[key]['description'],
                            result.leaves_balances_data[key]['balance'],
                            result.leaves_balances_data[key]['action'],
                          ])
                          .draw(true);
                    }
                    $('th#uq-leave').css({ display: 'none' });
                    $('#leaves-balances-employee-table').css({ width: '100%' });

					$('#form-leaves-balances-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-leaves-balances', function () {
		let form = document.getElementById('leaves_balances_form');
		let form_data = new FormData(form);
        
        let leaves_balances_employee = leaves_balances_employee_datatable.rows().data().toArray();
        let leaves_balances_employee_data = [];
        let leaves_balances_count_data = [];
        for (const lb of leaves_balances_employee) {
            leaves_balances_employee_data.push(lb[0]);
            leaves_balances_count_data.push(lb[3]);
        }
        
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.append('leaves_balances_employee[]', leaves_balances_employee_data);
        form_data.append('leaves_balances_count[]', leaves_balances_count_data);
        form_data.append('employee_id', $('#employee_id').val());
		
        let leave_balance_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', leave_balance_uuid);

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
                    
                    leaves_balances_datatable = initLeavesBalancesDataTable();

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
                
                $('#form-leaves-balances-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('click', '#add-leaves-balances-employee', function () {
        $.ajax({
            url : 'add-leaves-balances/', 
            method : 'POST', 
            data : {
                employee_id: $('#employee_id').val(),
                leave_id: $('#leave_id').val(),
                balance: $('#balance').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            }, 
            success:function(result){
                if (result.success === true) {
                    let leaves_data = [
                        result.leaves_data['uq_leave'],
                        result.leaves_data['name'],
                        result.leaves_data['description'],
                        result.leaves_data['balance'],
                        result.leaves_data['action'],
                    ];

                    let current_data = leaves_balances_employee_datatable.rows().data();

                    let is_exist = false;
                    for (const key of current_data.toArray()) {
                        if (key[0] === leaves_data[0]) {
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
                        
                        initLeavesBalancesEmployeeFooter();
                        leaves_balances_employee_datatable = initLeavesBalancesEmployeeDataTable(options_datatables);
                        leaves_balances_employee_datatable.row.add(leaves_data).draw(true);
                        
                    } else {
                        toastr['error']('Leave Already Exist');
                    }

                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error:function(result){
                
            }
        });
    });

     $('body').on('click', '.delete-leaves-balances-employee', function () {
        leaves_balances_employee_datatable.row($(this).parents('tr')).remove().draw();

    });

	$('#leaves-balances-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
