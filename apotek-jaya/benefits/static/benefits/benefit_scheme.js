$(function () {
    function format_number(num) {
        // Add a '.' after every 3 digits from the end of the input
        num = num.toString().replace(/\D/g, '');
        return num.replace(/(\d)(?=(\d{3})+$)/g, '$1.');
    }

	function initBenefitSchemeDataTable() {
		$('#benefit-scheme-table').DataTable().destroy();
		let benefit_scheme_datatable = $('#benefit-scheme-table').DataTable({
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
                url: 'scheme/fetch-benefit-scheme/',
                dataSrc: 'benefit_scheme_data',
            },
            responsive: true,
            columnDefs: [
                { targets: -1, width: '90px' },
                { targets: -2, width: '90px' }
            ],
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

        return benefit_scheme_datatable;
	}

	function initDetailBenefitsDataTable(options = { columnDefs :{}}) {
		$('#detail-benefits-table').DataTable().destroy();
		let detail_benefits_datatable = $('#detail-benefits-table').DataTable({
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

        return detail_benefits_datatable;
	}

    function initDetailBenefitsFooter() {
        $('#detail-benefits-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
        });
    }

	function initDetailEmployeesDataTable(options = { columnDefs :{}}) {
		$('#detail-employees-table').DataTable().destroy();
		let detail_employees_datatable = $('#detail-employees-table').DataTable({
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

        return detail_employees_datatable;
	}

    function initDetailEmployeesFooter() {
        $('#detail-employees-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
        });
    }

	function initDetailEmployeesListDataTable(options = { columnDefs :{}}) {
		$('#detail-employees-list-table').DataTable().destroy();
		let detail_employees_list_datatable = $('#detail-employees-list-table').DataTable({
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

        return detail_employees_list_datatable;
	}

    function initDetailEmployeesListFooter() {
        $('#detail-employees-list-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
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

    let detail_benefits_datatable = null;
    let detail_employees_list_datatable = null;
    let detail_employees_datatable = null;
	let benefit_scheme_datatable =  initBenefitSchemeDataTable();

	$('body').on('click', '.delete-benefit-scheme', function () {
		if (confirm('Do You Want to Deactivate this Benefit Scheme ?')) {
            let benefit_scheme_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', benefit_scheme_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        benefit_scheme_datatable = initBenefitSchemeDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-benefit-scheme, .view-benefit-scheme, #add-benefit-scheme', function () {
		let benefit_scheme_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', benefit_scheme_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-benefit-scheme-modal .modal-content').html(result.form);
                    
                    if (!result.is_view_only){
                        dselect(document.querySelector('select#benefit'), {
                            search: true,
                            clearable:true,
                        });

                        dselect(document.querySelector('select#department'), {
                            search: true,
                            clearable:true,
                        });
                    }
                    
                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                            { targets: 3, width: '30px', },
                            { targets: -1, width: '30px', },
                        ],
                    };

                    initDetailBenefitsFooter();
					detail_benefits_datatable = initDetailBenefitsDataTable(options_datatables);
                    
					for(const key in result.benefits_data){
						detail_benefits_datatable.row
                        .add([
							result.benefits_data[key]['uq_benefit'],
							result.benefits_data[key]['name'],
							result.benefits_data[key]['description'],
							result.benefits_data[key]['type_value'],
							'Rp. ' + format_number(result.benefits_data[key]['value']),
							result.benefits_data[key]['action'],
                        ])
                        .draw(true);
					}

                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                            { targets: -2, width: '60px', },
                            { targets: -1, width: '30px', },
                        ],
                    };

                    initDetailEmployeesFooter();
					detail_employees_datatable = initDetailEmployeesDataTable(options_datatables);
					for(const key in result.employees_data){
						detail_employees_datatable.row.add([
							result.employees_data[key]['uq_emp'],
							result.employees_data[key]['nik_email'],
							result.employees_data[key]['name'],
							result.employees_data[key]['address'],
							result.employees_data[key]['education'],
							result.employees_data[key]['department'],
							result.employees_data[key]['join_date'],
							result.employees_data[key]['expired_at'],
							result.employees_data[key]['status'],
							result.employees_data[key]['action'],

						]).draw(true);
					}

                    initDetailEmployeesListFooter();
                    detail_employees_list_datatable = initDetailEmployeesListDataTable();

                    $('#detail-benefits-table').css({ width: '100%' });
                    $('#detail-employees-list-table').css({ width: '100%' });
                    $('#detail-employees-table').css({ width: '100%' });
                    
                    if (!result.is_view_only){
                        $('#detail-benefits-table > tbody > tr').css({
                            'background-color': '#e9ecef',
                        });

                        $('#detail-employees-list-table > tbody > tr').css({
                            'background-color': '#e9ecef',
                        });

                        $('#detail-employees-table > tbody > tr').css({
                            'background-color': '#e9ecef',
                        });
                    }

                    $('th#uq-benefit').css({ display: 'none' });
                    $('th#uq-emp-dept').css({ display: 'none' });
                    $('th#uq-emp').css({ display: 'none' });

                    $('#form-benefit-scheme-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-benefit-scheme', function () {
        
		let form = document.getElementById('benefit_scheme_form');
		let form_data = new FormData(form);
        let cleaned_value = $('input#value').val();

        if (cleaned_value) cleaned_value = cleaned_value.replace(/\D/g, '');

        employees = detail_employees_datatable.rows().data().toArray();
        let employees_data = [];
        for (const emp of employees) {
            employees_data.push(emp[0]);
        }

        benefits = detail_benefits_datatable.rows().data().toArray();
        let benefits_data = [];
        let benefits_value = [];
        for (const ben of benefits) {
            benefits_data.push(ben[0]);
            let tmp = ben[4];
            tmp = tmp.match(/[\d+]/g);
            benefits_value.push(tmp.join(''));
        }
        
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.delete('value');
        form_data.append('value', cleaned_value);
        form_data.append('benefits[]', benefits_data);
        form_data.append('benefits_value[]', benefits_value);
        form_data.append('employees[]', employees_data);

		let benefit_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', benefit_uuid);
        
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

                    benefit_scheme_datatable = initBenefitSchemeDataTable();

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
                
                $('#form-benefit-scheme-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('click','.update-benefit-detail',function(){
        let current_row = $(this).closest('tr');
        let selected_row = current_row.find('td:eq(3)');
        
        if (selected_row.find('div.input-group').length === 0){
            let html_template = `
                <div class="input-group">
                    <input class="form-control input-form-update-benefit" type="text" value="${selected_row.text()}" />
                    <span class="input-group-text approve-benefit-detail" role="button">
                        <i class="fa-solid fa-check text-success"></i>
                    </span>
                </div>`;

            selected_row.html(html_template);
        }
    });

    $('body').on('click','.approve-benefit-detail',function(){
        let current_row = $(this).closest('tr');
        let selected_row = current_row.find('td:eq(3)');
        let selected_value = $(this).closest('.input-group').find('.input-form-update-benefit').val();
        
        $(this).closest('.input-group').remove();
        
        selected_row.html(selected_value);

        detail_benefits_datatable.row(`tr:eq(${current_row.index()})`).data()[4] = selected_value;
        detail_benefits_datatable.draw();

        toastr['success']('Benefit Detail Value Updated Succesfuly');
    });

    $('body').on('click', '#add-benefit-detail', function () {
        $.ajax({
            url: 'scheme/add-benefit-detail/',
            method: 'POST',
            data: {
                benefit: $('select#benefit').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (result) {
                if (result.success === true) {
                    let benefit_data = [
                      result.benefit_data['uq_benefit'],
                      result.benefit_data['name'],
                      result.benefit_data['description'],
                      result.benefit_data['type_value'],
                      'Rp. ' + format_number(result.benefit_data['value']),
                      result.benefit_data['action'],
                    ];

                    let current_data = detail_benefits_datatable.rows().data();

                    let is_exist = false;
                    for (const key of current_data.toArray()) {
                        if (key[0] === benefit_data[0]) {
                            is_exist = true;
                            break;
                        }
                    }

                    if (!is_exist) {
                        options_datatables = {
                            columnDefs: [
                                { targets: 0, visible: false, searchable: false, },
                                { targets: 3, width: '30px', },
                                { targets: -1, width: '30px', },
                            ],
                        };

                        detail_benefits_datatable = initDetailBenefitsDataTable(options_datatables);
                        detail_benefits_datatable.row.add(benefit_data).draw(true);
                        
                    } else {
                        toastr['error']('Benefit Already Exist in This Benefit Scheme');
                    }

                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error: function (result) {},
        });
    });

    $('body').on('click', '#show-employees-department', function () {
        $.ajax({
            url: 'scheme/show-employees-department/',
            method: 'POST',
            data: {
                department: $('select#department').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (result) {
                if (result.success === true) {
                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                            { targets: -2, width: '60px', },
                            { targets: -1, width: '30px', },
                        ],
                    };

                    initDetailEmployeesListFooter();
                    detail_employees_list_datatable = initDetailEmployeesListDataTable(options_datatables);
                    detail_employees_list_datatable.clear();
                    
                    let already_added_employees = detail_employees_datatable.rows().data().toArray();
                    
                    for (const emp in result.employees_data) {

                        let is_continue = false;
                        for (const key in already_added_employees) {
                            if ( result.employees_data[emp]['uq_emp'] === already_added_employees[key][0] ){
                                is_continue = true;
                                break;
                            }
                        }
                        
                        if (is_continue) 
                            continue;


                        let status = '<span class="badge bg-secondary">Unknown</span>';
                        if (result.employees_data[emp]['status'] === 1) {
                            status = '<span class="badge bg-success">Active</span>';

                        } else if (result.employees_data[emp]['status'] === 0) {
                            status = '<span class="badge bg-danger">Inactive</span>';

                        }

                            detail_employees_list_datatable.row
                            .add([
                                result.employees_data[emp]['uq_emp'],
                                result.employees_data[emp]['nik_email'],
                                result.employees_data[emp]['name'],
                                result.employees_data[emp]['address'],
                                result.employees_data[emp]['education'],
                                result.employees_data[emp]['department'],
                                result.employees_data[emp]['join_date'],
                                result.employees_data[emp]['expired_at'],
                                status,
                                result.employees_data[emp]['action'],
                            ])
                            .draw(true);
                        
                    }

                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error: function (result) {},
        });
    });

    $('body').on('click', '.delete-benefit-detail', function () {
        detail_benefits_datatable.row($(this).parents('tr')).remove().draw();

    });

    $('body').on('click', '.delete-employee-detail', function () {
        detail_employees_datatable.row($(this).parents('tr')).remove().draw();

    });

    $('body').on('click', '.add-employee-detail', function () {
        let added_employee = detail_employees_list_datatable.row($(this).parents('tr')).data();

        detail_employees_list_datatable.row($(this).parents('tr')).remove().draw();
        
        options_datatables = {
            columnDefs: [
                { targets: 0, visible: false, searchable: false, },
                { targets: -2, width: '60px', },
                { targets: -1, width: '30px', },
            ],
        };
        let trash_icon = `<div class='d-flex justify-content-center'>
                                <span class='delete-employee-detail btn text-danger w-100'>
                                    <i class="bi bi-trash"></i>
                                </span>
                            </div>`;
        
        added_employee[added_employee.length - 1] = trash_icon;
        detail_employees_datatable = initDetailEmployeesDataTable(options_datatables);
        detail_employees_datatable.row.add(added_employee).draw();
    });

    
    $('body').on('keyup','input#value, .input-form-update-benefit',function(){
        let current_value = $(this).val();
        $(this).val('Rp. ' + format_number(current_value));
    
    });

	$('#benefit-scheme-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});