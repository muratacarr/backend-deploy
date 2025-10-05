@router.post("/logout")
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and blacklist tokens"""
    try:
        # Blacklist the current access token
        TokenBlacklistService.add_token_to_blacklist(
            db=db,
            token=credentials.credentials,
            user_id=current_user.id,
            token_type="access"
        )
        
        # Log logout
        AuditService.log_action(
            db=db,
            action="logout",
            user_id=current_user.id,
            resource="auth",
            details={"email": current_user.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        logger.info(f"User {current_user.id} logged out successfully")
        
        return {
            "message": "Successfully logged out",
            "tokens_revoked": True
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/logout-all")
def logout_all_devices(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user from all devices (revoke all tokens)"""
    try:
        # Revoke all user tokens
        revoked_count = TokenBlacklistService.revoke_all_user_tokens(db, current_user.id)
        
        # Log logout all
        AuditService.log_action(
            db=db,
            action="logout_all_devices",
            user_id=current_user.id,
            resource="auth",
            details={"email": current_user.email, "tokens_revoked": revoked_count},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        logger.info(f"User {current_user.id} logged out from all devices, {revoked_count} tokens revoked")
        
        return {
            "message": "Successfully logged out from all devices",
            "tokens_revoked": revoked_count
        }
        
    except Exception as e:
        logger.error(f"Error during logout all: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout all devices failed"
        )
