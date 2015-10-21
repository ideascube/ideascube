function ServerAdmin(params) {

	if(confirm("Are you sure ?")){
		var form = document.forms["adminaction"];
		var hiddenField = document.createElement("input");

		hiddenField.setAttribute("type", "hidden");
		hiddenField.setAttribute("name", params);

		form.appendChild(hiddenField);
		form.submit();
	}
}