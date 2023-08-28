$(function () {
	function initBenefitCategoriesDataTable() {
		$('#benefit-categories-table').DataTable().destroy();
		let benefit_categories_datatable = $('#benefit-categories-table').DataTable({
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
                url: 'category/fetch-benefit-categories/',
                dataSrc: 'benefit_categories_data',
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

        return benefit_categories_datatable;
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

	let benefit_categories_datatable =  initBenefitCategoriesDataTable();

	$('body').on('click', '.delete-benefit-categories', function () {
		if (confirm('Do You Want to Deactivate this Benefit Categories ?')) {
            let benefit_category_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', benefit_category_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        benefit_categories_datatable = initBenefitCategoriesDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-benefit-categories, .view-benefit-categories, #add-benefit-categories', function () {
		let benefit_category_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', benefit_category_uuid);
		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-benefit-categories-modal .modal-content').html(result.form);
                    
                    $('#form-benefit-categories-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-benefit-categories', function () {
        
		let form = document.getElementById('benefit_categories_form');
		let form_data = new FormData(form);

        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

		let benefit_categories_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', benefit_categories_uuid);
        
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

                    benefit_categories_datatable = initBenefitCategoriesDataTable();

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
                
                $('#form-benefit-categories-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

	$('#benefit-categories-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});