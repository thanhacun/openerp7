 -- alter TABLE kderp_asset_management ADD column remaining_amount numeric;
 -- alter TABLE kderp_asset_management ADD column using_remaining boolean;
 begin;
 Update kderp_asset_management kam set remaining_amount=amount,using_remaining=True from kderp_asset_remaining kar where kam.code=kar.newcode;
 rollback;
