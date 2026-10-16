terraform {
  backend "oci" {
    # Legacy resource name retained so the existing remote state is not migrated.
    bucket    = "cloud-playground-terraform-state-file"
    namespace = "axwj7qxpzppm"
    key       = "oci-free-vm/terraform.tfstate"
    region    = "ap-hyderabad-1"
  }
}
