create or replace trigger tri_name
  before insert on table_name  
  for each row
declare
  -- local variables here
begin
  select SEQ_NAME.nextval into :new.ID from dual;
end tri_name;
/
