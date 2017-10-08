import tensorflow as tf

from differential_privacy.dp_sgd.dp_optimizer import sanitizer as san


def ComputeBaselinePrincipalProjection(data, projection_dims):
  """Compute baseline projection.

  Args:
    data: the input data, each row is a data vector.
    projection_dims: the projection dimension.

  Returns:
    A projection matrix with projection_dims columns.
  """

  # Normalize each row.
  normalized_data = tf.nn.l2_normalize(data, 1)
  covar = tf.matmul(tf.transpose(normalized_data), normalized_data)
  saved_shape = tf.shape(covar)
  num_examples = tf.slice(tf.shape(data), [0], [1])
  if eps > 0:
    # Since the data is already normalized, there is no need to clip
    # the covariance matrix.
    assert delta > 0
    saned_covar = sanitizer.sanitize(
        tf.reshape(covar, [1, -1]), eps_delta, sigma=sigma,
        option=san.ClipOption(1.0, False), num_examples=num_examples)
    saned_covar = tf.reshape(saned_covar, saved_shape)
    # Symmetrize saned_covar. This also reduces the noise variance.
    saned_covar = 0.5 * (saned_covar + tf.transpose(saned_covar))
  else:
    saned_covar = covar

  # Compute the eigen decomposition of the covariance matrix, and
  # return the top projection_dims eigen vectors, represented as columns of
  # the projection matrix.
  eigvals, eigvecs = tf.self_adjoint_eig(saned_covar)
  _, topk_indices = tf.nn.top_k(eigvals, projection_dims)
  topk_indices = tf.reshape(topk_indices, [projection_dims])
  # Gather and return the corresponding eigenvectors.
  return tf.transpose(tf.gather(tf.transpose(eigvecs), topk_indices))