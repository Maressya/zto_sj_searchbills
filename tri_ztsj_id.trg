create or replace trigger tri_ztsj_id
  before insert on datawork_zt_sj_all_orc  
  for each row
declare
  -- local variables here
begin
  select SEQ_ZTSJ_ID.nextval into :new.ID from dual;
end tri_ztsj_id;
/
