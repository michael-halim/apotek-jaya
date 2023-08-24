$(function () {
    function format_number(num) {
        // Add a '.' after every 3 digits from the end of the input
        num = num.toString().replace(/\D/g, '');
        num = num.toString().replace(/^(0{1,})(\d+)/g, '$2');
        num = num.replace(/(\d)(?=(\d{3})+$)/g, '$1.')
        if (num == '') num = '0';
            
        return num
    }

    function fetch_salary_filter(){
        $.ajax({
            url : 'fetch-period/', 
            method : 'GET', 
            data : {
                
            }, 
            success:function(result){
                let option = '<option value="---------">---------</option>';
                if (result['success']){
                    for (data of result['payroll_periods_data']){
                        option += `<option value="${data['hash']}">${data['name']}</option>`;
                    }
                }
                $('#period-filter').html(option);
            },
            error:function(result){
                
            }
        });
    }

    function fetch_departments_filter(){
        $.ajax({
            url : 'fetch-departments/', 
            method : 'GET', 
            data : {
                
            }, 
            success:function(result){
                let option = '<option value="---------">---------</option>';
                if (result['success']){
                    for (data of result['departments_data']){
                        option += `<option value="${data['hash']}">${data['name']}</option>`;
                    }
                }
                $('#departments-filter').html(option);
            },
            error:function(result){
                
            }
        });
    }
    function initSalaryComponentsDataTable(options = { columnDefs :{}}) {
		$('#salary-components-table').DataTable().destroy();
		let salary_components_datatable = $('#salary-components-table').DataTable({
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
            responsive: true,
            columnDefs: options.columnDefs,
		});

        return salary_components_datatable;
	}

    function initSalaryComponentsFooter() {
        $('#salary-components-table tfoot th.search-text').each(function () {
            var title = $(this).text();
            $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
        });
    }

	function initSalariesDataTable(fetch_url) {
		$('#salaries-table').DataTable().destroy();
		let salaries_datatable = $('#salaries-table').DataTable({
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
                url: fetch_url,
                dataSrc: 'salaries_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width: '90px' }],
            columns: [
                {
                    data: 'nik_name',
                    defaultContent: '-',
                },
                {
                    data: 'department',
                    defaultContent: '-',
                },
                {
                    data: 'gross_salary',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'final_salary',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
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

        return salaries_datatable;
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

    let salaries_period_filter = fetch_salary_filter();
    let salaries_departmets_filter = fetch_departments_filter();
	let salaries_datatable = initSalariesDataTable(fetch_url='fetch-salaries/');
    let salary_components_datatable = null;
    let current_period_filter = null;
    let current_dept_filter = null;

    $('body').on('click', '.delete-salaries', function () {
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();

		if (confirm('Do You Want to Deactivate this Salaries ?')) {
            let salary_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', salary_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        salaries_datatable = initSalariesDataTable(fetch_url='fetch-salaries/');
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-salaries, .view-salaries, #add-salaries', function () {
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();

		let salary_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', salary_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {

					$('#form-salaries-modal .modal-content').html(result.form);
                    
                    // Format Number
                    let inputs = [
                        'gross_salary', 'ptkp', 'final_salary',
                        'base_salary', 'allowance', 'bonus',
                        'pph21', 'overtime_hours_nominal', 'deduction', 'thr'
                    ];

                    for (const input_name of inputs){
                        $(`input#${input_name}`).val('Rp. ' + format_number($(`input#${input_name}`).val()));
                    }

                    options_datatables = {
                        columnDefs: [
                            { targets: 0, visible: false, searchable: false, },
                            { targets: 3, width: '30px', },
                            { targets: -1, width: '30px', },
                        ],
                    };

                    initSalaryComponentsFooter();
					salary_components_datatable = initSalaryComponentsDataTable(options_datatables);
                    
					for(const key in result.salary_components_data){
						salary_components_datatable.row
                        .add([
							result.salary_components_data[key]['uq_benefit'],
							result.salary_components_data[key]['name'],
							result.salary_components_data[key]['benefit_scheme'],
							result.salary_components_data[key]['is_benefit_adjustment'],
							result.salary_components_data[key]['description'],
							result.salary_components_data[key]['type_value'],
							'Rp. ' + format_number(result.salary_components_data[key]['value']),
							result.salary_components_data[key]['action'],
                        ])
                        .draw(true);
					}
                    
                    $('#salary-components-table').css({ width: '100%' });
                    
                    if (!result.is_view_only){
                        $('#salary-components-table > tbody > tr').css({
                            'background-color': '#e9ecef',
                        });

                    }

                    $('th#uq-benefit').css({ display: 'none' });

					$('#form-salaries-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-salaries', function () {
		let form = document.getElementById('salaries_form');
		let form_data = new FormData(form);
        let inputs = [
            'gross_salary', 'ptkp', 'final_salary',
            'base_salary', 'allowance', 'bonus',
            'pph21', 'overtime_hours_nominal', 'deduction', 'thr'
        ];

        let cleaned_inputs = {};

        for (const input of inputs){
            let input_val =  $('input#' + input).val();
            if (input_val) cleaned_inputs[input] = input_val.replace(/\D/g, '');
        }

        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        
        for (const input of inputs){
            form_data.delete(input);
            form_data.append(input, cleaned_inputs[input]);
        }
        
        let salary_components = [];
        for (const data of salary_components_datatable.rows().data().toArray()){
            salary_components.push(data[0]);
        }

        form_data.append('salary_components[]', salary_components);

		let salary_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', salary_uuid);

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

                    salaries_datatable = initSalariesDataTable(fetch_url=`fetch-salaries/?pu=${current_period_filter}&du=${current_dept_filter}`);

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
                
                $('#form-salaries-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('change','#period-filter, #departments-filter', function(){
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();
        
        salaries_datatable = initSalariesDataTable(fetch_url=`fetch-salaries/?pu=${current_period_filter}&du=${current_dept_filter}`);
    });

    $('body').on('click', '.delete-salary-components', function () {
        salary_components_datatable.row($(this).parents('tr')).remove().draw();
    });

    $('body').on('click', '#add-salary-adjustment', function () {
        let salary_uuid = $(this).data('uq');
        let cleaned_salary_adjustment_value = $('#value').val().replace(/\D/g, '');
        $.ajax({
            url : 'add-salary-adjustment/', 
            method : 'POST', 
            data : {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                name: $('#name').val(),
                description: $('#description').val(),
                is_deduction: $('#is_deduction').is(":checked"),
                value: cleaned_salary_adjustment_value,
                salary_uuid: salary_uuid,
            }, 
            success:function(result){
                console.log(result);
                if (result.success === true) {
                    for(const key in result.salary_components_data){
                        salary_components_datatable.row
                        .add([
                            result.salary_components_data[key]['uq_benefit'],
                            result.salary_components_data[key]['name'],
                            result.salary_components_data[key]['benefit_scheme'],
                            result.salary_components_data[key]['is_benefit_adjustment'],
                            result.salary_components_data[key]['description'],
                            result.salary_components_data[key]['type_value'],
                            'Rp. ' + format_number(result.salary_components_data[key]['value']),
                            result.salary_components_data[key]['action'],
                        ])
                        .draw(true);
                    }

                    $('#salary-components-table').css({ width: '100%' });
                    $('th#uq-benefit').css({ display: 'none' });

                    toastr['success'](result.toast_message);

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

                $('#form-salaries-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error:function(result){
                
            }
        });
    });

    $('body').on('click','#calculate-salary',function(){
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();

        $.ajax({
            url: 'calculate-salaries/',
            method: 'POST',
            data: {
                period_uuid: current_period_filter,
                dept_uuid: current_dept_filter,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (result) {
                if (result.success === true) {
                    salaries_datatable = initSalariesDataTable(fetch_url=`fetch-salaries/?pu=${current_period_filter}&&du=${current_dept_filter}`);
                    
                    toastr['success'](result.toast_message);

                } else if (result.success === false) {
                    toastr['error'](result.toast_message);
                }
            },
            error: function (result) {},
        });
    });
    
    $('body').on('keyup','input#gross_salary, input#ptkp, input#final_salary, input#base_salary, input#allowance, input#bonus, input#pph21, input#overtime_hours_nominal, input#deduction, input#value, input#thr',function(){
        let current_value = $(this).val();
        $(this).val('Rp. ' + format_number(current_value));
    
    });

	$('#salaries-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
