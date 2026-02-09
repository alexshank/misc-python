## KMS

- Anytime you hear encryption, think Key Management Service
- You'd use an asymetric key if you have users who need to perform encryptions, but do not have the ability to make KMS service API calls.
- envelope encryption - data keys and wrapping keys
- keyrings - generate, encrypt, and decrypt data keys
- master key provider (alternative) - returns the wrapping keys you specify
- best practice to specify wrapping keys during decryption
- CloudHSM (Hardsare Security Module) for custom key stores
- External = BYOK
  - automatic rotation is NOT supported
  - four step process for importing an external key to KMS
- multi region keys are NOT global keys
