function displayImages(images)
{
  console.log(images);
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '';
  if (Array.isArray(images) && images.length > 0)
  {
    images.forEach(imageUrl =>
    {
      const img = document.createElement('img');
      img.src = imageUrl;
      img.style.width = '200px';
      img.style.margin = '5px';
      resultDiv.appendChild(img);
    });
  } else
  {
    resultDiv.textContent = 'No images available';
  }
}

function handleApiResponse(response)
{
  return response.json().then(data =>
  {
    if (!response.ok)
    {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    return data;
  });
}

document.addEventListener('DOMContentLoaded', function ()
{
  // 直接从 S3 获取图片列表
  fetch('https://soulmind-image-generator.s3.amazonaws.com/?list-type=2&prefix=generated-images/')
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "text/xml"))
    .then(data =>
    {
      const images = Array.from(data.querySelectorAll('Contents'))
        .filter(el => el.querySelector('Key').textContent.toLowerCase().endsWith('.png'))
        .map(el => `https://soulmind-image-generator.s3.amazonaws.com/${el.querySelector('Key').textContent}`);
      displayImages(images);
    })
    .catch(error =>
    {
      console.error('Fetch error:', error);
      document.getElementById('result').textContent = `Error fetching images: ${error.message}`;
    });
});

document.getElementById('generate').addEventListener('click', function ()
{
  const prompt = document.getElementById('prompt').value;
  const tags = Array.from(document.querySelectorAll('#tags input:checked')).map(el => el.value);

  // 显示加载指示器
  const resultDiv = document.getElementById('result');
  resultDiv.textContent = 'Generating image, please wait...';

  fetch('https://xo4tmk9edc.execute-api.us-west-1.amazonaws.com/prod/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt, tags }),
  })
    .then(handleApiResponse)
    .then(data =>
    {
      console.log('Generate response:', data);
      if (data.image_url)
      {
        // 清除加载消息
        resultDiv.textContent = '';
        const img = document.createElement('img');
        img.src = data.image_url;
        img.style.width = '200px';
        img.style.margin = '5px';
        resultDiv.insertBefore(img, resultDiv.firstChild);
      } else
      {
        throw new Error('No image URL in response');
      }
    })
    .catch(error =>
    {
      console.error('Error:', error);
      resultDiv.textContent = `An error occurred: ${error.message}`;
    });
});