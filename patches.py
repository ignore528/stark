
def apply():
    import pyrogram.errors.exceptions.forbidden_403 as _f403
    import pyrogram.errors.exceptions.bad_request_400 as _f400
    import pyrogram.errors.exceptions as _exc
    import pyrogram.errors as _err

    if not hasattr(_f403, "GroupcallForbidden"):
        class GroupcallForbidden(_f403.Forbidden):
            ID = "GROUPCALL_FORBIDDEN"
            MESSAGE = __doc__
        _f403.GroupcallForbidden = GroupcallForbidden
        _exc.GroupcallForbidden = GroupcallForbidden
        _err.GroupcallForbidden = GroupcallForbidden

    if not hasattr(_err, "GroupcallInvalid"):
        _err.GroupcallInvalid = _err.GroupCallInvalid
        _exc.GroupcallInvalid = _err.GroupCallInvalid

    import pyrogram.raw.types as _rty

    if not hasattr(_rty, "InputGroupCallSlug"):
        from pyrogram.raw.types.input_group_call_slug import InputGroupCallSlug
        _rty.InputGroupCallSlug = InputGroupCallSlug

    if not hasattr(_rty, "PhoneCallDiscardReasonMigrateConferenceCall"):
        from pyrogram.raw.types.phone_call_discard_reason_migrate_conference_call import (
            PhoneCallDiscardReasonMigrateConferenceCall,
        )
        _rty.PhoneCallDiscardReasonMigrateConferenceCall = PhoneCallDiscardReasonMigrateConferenceCall

apply()
