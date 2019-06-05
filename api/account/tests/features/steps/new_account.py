from binascii import b2a_base64
from datetime import date
import os

import stripe
from behave import given, then, when
from flask import json
from hamcrest import assert_that, equal_to, is_in, none, not_none, starts_with
from stripe.error import InvalidRequestError

from selene.data.account import AccountRepository, PRIVACY_POLICY, TERMS_OF_USE
from selene.util.db import connect_to_db

new_account_request = dict(
    username='barfoo',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedPlatform=None,
        federatedToken=None,
        userEnteredEmail=b2a_base64(b'bar@mycroft.ai').decode(),
        password=b2a_base64(b'bar').decode()
    ),
    support=dict(openDataset=True)
)


@given('a user completes on-boarding')
def build_new_account_request(context):
    context.new_account_request = new_account_request


@given('user opts out of membership')
def add_maybe_later_membership(context):
    context.new_account_request['support'].update(
        membership=None,
        paymentMethod=None,
        paymentAccountId=None
    )


@given('user opts into a membership')
def change_membership_option(context):
    context.new_account_request['support'].update(
        membership='Monthly Membership',
        paymentMethod='Stripe',
        paymentToken='tok_visa'
    )


@given('user does not specify an email address')
def remove_email_from_request(context):
    del(context.new_account_request['login']['userEnteredEmail'])


@when('the new account request is submitted')
def call_add_account_endpoint(context):
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application/json'
    )


@then('the account will be added to the system {membership_option}')
def check_db_for_account(context, membership_option):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    acct_repository = AccountRepository(db)
    account = acct_repository.get_account_by_email('bar@mycroft.ai')
    assert_that(account, not_none())
    assert_that(
        account.email_address, equal_to('bar@mycroft.ai')
    )
    assert_that(account.username, equal_to('barfoo'))
    if membership_option == 'with a membership':
        assert_that(account.membership.type, equal_to('Monthly Membership'))
        assert_that(
            account.membership.payment_account_id,
            starts_with('cus')
        )
    elif membership_option == 'without a membership':
        assert_that(account.membership, none())

    assert_that(len(account.agreements), equal_to(2))
    for agreement in account.agreements:
        assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
        assert_that(agreement.accept_date, equal_to(str(date.today())))


@when('the account is deleted')
def account_deleted(context):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    acct_repository = AccountRepository(db)
    account = acct_repository.get_account_by_email('bar@mycroft.ai')
    context.stripe_id = account.membership.payment_id
    context.response = context.client.delete('/api/account')


@then('he membership is removed from stripe')
def check_stripe(context):
    stripe_id = context.stripe_id
    assert_that(stripe_id, not_none())
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    subscription_not_found = False
    try:
        stripe.Subscription.retrieve(stripe_id)
    except InvalidRequestError:
        subscription_not_found = True
    assert_that(subscription_not_found, equal_to(True))
