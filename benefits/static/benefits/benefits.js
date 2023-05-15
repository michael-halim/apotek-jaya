$(function () {
	function initBenefitsDataTable() {
		$('#benefits-table').DataTable().destroy();
		let benefit_datatable = $('#benefits-table').DataTable({
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
                url: 'fetch-benefits/',
                dataSrc: 'benefits_data',
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
                    data: 'value',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + data.toString().replace(/(\d)(?=(\d{3})+$)/g, '$1.');
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
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
		});

        return benefit_datatable;
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
    
	let benefit_datatable =  initBenefitsDataTable();

	$('body').on('click', '.delete-benefits', function () {
		if (confirm('Do You Want to Deactivate this Benefits ?')) {
            let benefit_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', benefit_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        benefit_datatable = initBenefitsDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-benefits, .view-benefits, #add-benefits', function () {
		let benefit_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', benefit_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
                    console.log(result);
					$('#form-benefits-modal .modal-content').html(result.form);

                    let value = $('input#value').val();
                    value = value.replace(/(\d)(?=(\d{3})+$)/g, '$1.');
                    $('input#value').val(value);

					$('#form-benefits-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-benefits', function () {
		let form = document.getElementById('benefits_form');
		let form_data = new FormData(form);
        let cleaned_value = $('input#value').val().replace(/\D/g, '');

        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.delete('value');
        form_data.append('value', cleaned_value);

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

                    benefit_datatable = initBenefitsDataTable();

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
                
                $('#form-benefits-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('keyup','input#value',function(){
        let current_value = $(this).val().replace(/\D/g, '');

        // Add a '.' after every 3 digits from the end of the input
        current_value = current_value.replace(/(\d)(?=(\d{3})+$)/g, '$1.');

        $(this).val(current_value);
    
    });

	$('#benefits-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
