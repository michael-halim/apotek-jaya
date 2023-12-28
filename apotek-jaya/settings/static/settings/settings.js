$(function () {
    function format_number(num) {
        // Add a '.' after every 3 digits from the end of the input
        num = num.toString().replace(/\D/g, '');
        num = num.toString().replace(/^(0{1,})(\d+)/g, '$2');
        num = num.replace(/(\d)(?=(\d{3})+$)/g, '$1.')
        if (num == '') num = '0';
            
        return num
    }

	function initSettingsDataTable() {
		$('#settings-table').DataTable().destroy();
		let settings_datatable = $('#settings-table').DataTable({
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
                url: 'fetch-settings/',
                dataSrc: 'settings_data',
            },
            responsive: true,
            columnDefs: [],
            columns: [
                {
                    data: 'overtime_rate',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'lembur_rate',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'uq',
                },
            ],
		});

        return settings_datatable;
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

	let settings_datatable =  initSettingsDataTable();
	
	$('body').on('click','.update-settings, .view-settings, #add-settings', function () {
		let url = $(this).data('link');
		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-settings-modal .modal-content').html(result.form);

                    $('input#overtime_rate').val('Rp. ' + format_number($('input#overtime_rate').val()));
                    $('input#lembur_rate').val('Rp. ' + format_number($('input#lembur_rate').val()));

                    $('#form-settings-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-settings', function () {
        let form = document.getElementById('settings_form');
		let form_data = new FormData(form);
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        if ($('input#overtime_rate').val() !== undefined) {
            form_data.delete('overtime_rate');
            form_data.append('overtime_rate', $('input#overtime_rate').val().replace(/\D/g, ''));
        }
        
        if ($('input#lembur_rate').val() !== undefined) {
            form_data.delete('lembur_rate');
            form_data.append('lembur_rate', $('input#lembur_rate').val().replace(/\D/g, ''));
        }
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

                    settings_datatable = initSettingsDataTable();
                    $('#add-settings').html('');

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
                
                $('#form-settings-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});
    
    $('body').on('keyup','input#overtime_rate, input#lembur_rate',function(){
        let current_value = $(this).val();
        $(this).val('Rp. ' + format_number(current_value));
    
    });

	$('#settings-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});