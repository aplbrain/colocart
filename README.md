<p align=center>🛒</p>
<h3 align=center>c o l o c a r t</h3>
<h6 align=center>A simple build system for static-site deploys.</h6>


## Installation

```shell
git clone https://github.com/aplbrain/colocart.git
cd colocart
pip3 install -U .
```

## Usage

```shell
colocart build .
colocart deploy .
```

You may want to specify an AWS profile-name:

```shell
AWS_PROFILE=aplbrain colocart deploy .
```

## Example

For a yarn-built npm project:

`colocart.cfg`:
```
[BUILD]
BuildCommand = "yarn run build"
BuildDirectory = dist

[UPLOAD]
BucketName = my-s3-bucket
```
