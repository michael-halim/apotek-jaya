$(function () {
	function initPayrollPeriodDataTable() {
		$('#payroll-periods-table').DataTable().destroy();
		let payroll_periods_datatable = $('#payroll-periods-table').DataTable({
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
                url: 'fetch-payroll-period/',
                dataSrc: 'payroll_periods_data',
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

        return payroll_periods_datatable;
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

	let payroll_periods_datatable = initPayrollPeriodDataTable();

	$('body').on('click', '.delete-payroll-periods', function () {
		if (confirm('Do You Want to Deactivate this Payroll Period ?')) {
            let period_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', period_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        payroll_periods_datatable = initPayrollPeriodDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-payroll-periods, .view-payroll-periods, #add-payroll-periods', function () {
		let period_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', period_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-payroll-periods-modal .modal-content').html(result.form);

					$('#form-payroll-periods-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

    $('body').on('click','#import-payroll-periods', function () {
		let url = $(this).data('link');

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-payroll-periods-modal .modal-content').html(result.form);

					$('#form-payroll-periods-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-payroll-periods', function () {
		let form = document.getElementById('payroll_periods_form');
		let form_data = new FormData(form);

        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

		let period_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', period_uuid);

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

                    payroll_periods_datatable = initPayrollPeriodDataTable();

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
                
                $('#form-payroll-periods-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

	$('#payroll-periods-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
