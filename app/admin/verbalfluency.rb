ActiveAdmin.register Verbalfluency do

permit_params :subject_id, :study_id, :date, :visit_num, :form, :response1, :correct_responses1, :repititions1, :violations1, :response2, :correct_responses2, :repititions2, :violations2, :response3, :correct_responses3, :repititions3, :violations3, :response4, :correct_responses4, :repititions4, :violations4, :administrator, :entered_by, :verified_by

index do
    id_column
    column :subject_id
    column :date
    column :study_id
    column :visit_num
    column :administrator
    actions
end

form do |f|
    f.semantic_errors
    f.inputs do
        f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
        datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
        } 
        f.input :subject, :label => "Subject ID"
        f.input :study_id
        f.input :visit_num
        f.input :form
        f.input :response1
        f.input :correct_responses1
        f.input :repititions1
        f.input :violations1
        f.input :response2
        f.input :correct_responses2
        f.input :repititions2
        f.input :violations2
        f.input :response3
        f.input :correct_responses3
        f.input :repititions3
        f.input :violations3
        f.input :response4
        f.input :correct_responses4
        f.input :repititions4
        f.input :violations4
        f.input :administrator
        f.input :entered_by
        f.input :verified_by
    end
    f.actions
end
end
    