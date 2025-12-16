ActiveAdmin.register Techinventory do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :labidnumber, :itemdescription, :itembrand, :itemserialnumber, :itemroom, :itemlocation, :createddate, :createdby, :updateddate, :updatedby
  #
  # or
  #
  # permit_params do
  #   permitted = [:labidnumber, :itemdescription, :itembrand, :itemserialnumber, :itemroom, :itemlocation, :createddate, :createdby, :updateddate, :updatedby]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  form do |f|
    f.semantic_errors
    f.inputs  do
      f.input :labidnumber
      f.input :itemdescription
      f.input :itembrand
      f.input :itemserialnumber
      f.input :itemroom
      f.input :itemlocation
      f.input :createddate, :label => "Date Created",
                as: :datepicker,
                      datepicker_options: {
                        min_date: "1900-01-01",
                        max_date: "+3D"
                      } 
      f.input :createdby
      f.input :updateddate, :label => "Date Updated (yyyy-mm-dd)",
                as: :datepicker,
                      datepicker_options: {
                        min_date: "1900-01-01",
                        max_date: "+3D"
                      } 
      f.input :updatedby
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end

index do
  id_column
  column :labidnumber
  column :itemdescription
  column :itembrand
  column :itemserialnumber
  column :itemroom
  column :itemlocation
  column :createddate
  column :createdby
  actions
end
# filter :labidnumber
# filter :itemserialnumber
# filter :itemroom
# filter :itemlocation
# filter :createdby
# filter :updatedby
end
